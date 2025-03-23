from __future__ import annotations

from agents import HandoffOutputItem
from agents import ItemHelpers
from agents import MessageOutputItem
from agents import RunItem
from agents import Runner
from agents import ToolCallItem
from agents import ToolCallOutputItem
from loguru import logger
from telegram import Message
from telegram import Update
from telegram.ext import ContextTypes

from bot.utils import async_load_url

from ..cache import get_cache_from_env
from ..callbacks.utils import get_message_text
from ..utils import parse_url
from . import get_default_agent
from . import get_fortune_teller_agent


def log_run_items(items: list[RunItem]) -> None:
    for item in items:
        agent_name = item.agent.name
        if isinstance(item, MessageOutputItem):
            logger.info("{}: {}", agent_name, ItemHelpers.text_message_output(item))
        elif isinstance(item, HandoffOutputItem):
            logger.info("Handed off from {} to {}", item.source_agent.name, item.target_agent.name)
        elif isinstance(item, ToolCallItem):
            logger.info("{}: Calling a tool", agent_name)
        elif isinstance(item, ToolCallOutputItem):
            logger.info("{}: Tool call output: {}", agent_name, item.output)
        else:
            logger.info("{}: Skipping item: {}", agent_name, item.__class__.__name__)


class MultiAgentService:
    def __init__(self, max_cache_size: int = 100) -> None:
        self.max_cache_size = max_cache_size

        self.furtune_teller_agent = get_fortune_teller_agent()
        self.default_agent = get_default_agent()

        # self.default_agent.handoffs = [self.furtune_teller_agent]
        # self.furtune_teller_agent.handoffs = [self.default_agent]

        self.current_agent = self.default_agent

        # message.chat.id -> list of messages
        self.cache = get_cache_from_env()

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

        # log the new items
        log_run_items(result.new_items)

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

        await self.handle_message(message, include_reply_to_message=False)

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
