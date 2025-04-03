from __future__ import annotations

import textwrap

from agents import Agent
from agents import HandoffOutputItem
from agents import ItemHelpers
from agents import MessageOutputItem
from agents import RunItem
from agents import Runner
from agents import ToolCallItem
from agents import ToolCallOutputItem
from agents.items import ResponseFunctionToolCall
from agents.mcp import MCPServerStdio
from loguru import logger
from telegram import Message
from telegram import Update
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler
from telegram.ext import filters

from bot.utils import async_load_url

from ..agents.model import get_openai_model
from ..agents.model import get_openai_model_settings
from ..cache import get_cache_from_env
from ..callbacks.utils import get_message_text
from ..config import AgentServiceParams
from ..utils import parse_url
from . import get_default_agent


def shorten_text(text: str, width: int = 100, placeholder: str = "...") -> str:
    return textwrap.shorten(text, width=width, placeholder=placeholder)


def log_new_items(new_items: list[RunItem]) -> None:
    for new_item in new_items:
        if isinstance(new_item, MessageOutputItem):
            logger.info("Message: {}", shorten_text(ItemHelpers.text_message_output(new_item)))
        elif isinstance(new_item, HandoffOutputItem):
            logger.info(
                "Handed off from {} to {}",
                new_item.source_agent.name,
                new_item.target_agent.name,
            )
        elif isinstance(new_item, ToolCallItem):
            if isinstance(new_item.raw_item, ResponseFunctionToolCall):
                logger.info("Calling tool: {}({})", new_item.raw_item.name, new_item.raw_item.arguments)
        elif isinstance(new_item, ToolCallOutputItem):
            logger.info("Tool call output: {}", shorten_text(str(new_item.raw_item["output"])))
        else:
            logger.info("Skipping item: {}", new_item.__class__.__name__)


class AgentService:
    def __init__(self, params: AgentServiceParams, max_cache_size: int = 100) -> None:
        self.command = params["command"]
        self.help = params["help"]
        self.agents = [
            Agent(
                name=params["agent"]["name"],
                instructions=params["agent"]["instructions"],
                model=get_openai_model(),
                model_settings=get_openai_model_settings(),
                mcp_servers=[MCPServerStdio(params=p) for p in params["agent"]["mcp_servers"].values()],
            )
        ]
        if not self.agents:
            logger.info("No agents found in config, using default agent")
            self.agents = [get_default_agent()]
        self.current_agent = self.agents[0]

        # max_cache_size is the maximum number of messages to keep in the cache
        self.max_cache_size = max_cache_size

        # message.chat.id -> list of messages
        self.cache = get_cache_from_env()

    def get_command_handler(self, filters: filters.BaseFilter) -> CommandHandler:
        return CommandHandler(command=self.command, callback=self.handle_command, filters=filters)

    def get_message_handler(self, filters: filters.BaseFilter) -> MessageHandler:
        return MessageHandler(filters=filters, callback=self.handle_reply)

    async def handle_message(self, message: Message, include_reply_to_message: bool = False) -> None:
        message_text = get_message_text(
            message,
            include_reply_to_message=include_reply_to_message,
            include_user_name=True,
        )
        if not message_text:
            return

        # Get the memory for the current chat (group or user)
        key = f"bot:{message.chat.id}"
        messages = await self.cache.get(key)
        if messages is None:
            messages = []
            logger.info("No key found for {}", key)

        # replace the URL with the content
        parsed_url = parse_url(message_text)
        if parsed_url:
            url_content = await async_load_url(parsed_url)
            message_text = message_text.replace(
                parsed_url,
                f"[URL content from {parsed_url}]:\n'''\n{url_content}\n'''\n[END of URL content]\n",
                1,
            )

        # add the user message to the list of messages
        messages.append(
            {
                "role": "user",
                "content": message_text,
            }
        )

        # send the messages to the agent
        result = await Runner.run(self.current_agent, input=messages)

        log_new_items(result.new_items)

        # update the memory
        input_items = result.to_input_list()
        if len(input_items) > self.max_cache_size:
            input_items = input_items[-self.max_cache_size :]
        await self.cache.set(key, input_items)

        # update the current agent
        self.current_agent = result.last_agent

        await message.reply_text(result.final_output)

    async def handle_command(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        message = update.message
        if not message:
            return

        await self.handle_message(message, include_reply_to_message=True)

    async def handle_reply(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        # TODO: Implement filters.MessageFilter for reply to bot

        message = update.message
        if not message:
            return

        reply_to_message = message.reply_to_message
        if not reply_to_message:
            return

        from_user = reply_to_message.from_user
        if not from_user:
            return

        if not from_user.is_bot:
            return

        await self.handle_message(message, include_reply_to_message=True)
