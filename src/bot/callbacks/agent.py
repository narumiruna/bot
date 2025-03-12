from __future__ import annotations

import os

from agents import Agent
from agents import HandoffOutputItem
from agents import ItemHelpers
from agents import MessageOutputItem
from agents import ModelSettings
from agents import OpenAIChatCompletionsModel
from agents import Runner
from agents import ToolCallItem
from agents import ToolCallOutputItem
from agents import TResponseInputItem
from agents import set_default_openai_client
from agents import set_default_openai_key
from agents import set_tracing_disabled
from loguru import logger
from openai import AsyncAzureOpenAI
from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import ContextTypes

from ..tools.openai_agents import get_current_time
from ..tools.openai_agents import query_ticker_from_yahoo_finance
from .utils import get_message_text


def get_openai_client() -> AsyncOpenAI:
    azure_api_key = os.getenv(key="AZURE_OPENAI_API_KEY")
    if azure_api_key is not None:
        logger.info("Using Azure OpenAI API")

        openai_client = AsyncAzureOpenAI(api_key=azure_api_key)
        set_default_openai_key(azure_api_key)
        set_default_openai_client(openai_client)

        # Disable tracing since Azure doesn't support it
        set_tracing_disabled(True)
    else:
        openai_client = AsyncOpenAI()
    return openai_client


class MultiAgentService:
    def __init__(self, memory_window: int = 100) -> None:
        self.openai_client = get_openai_client()
        self.memory_window = memory_window

        self.model_settings = ModelSettings(
            temperature=float(os.getenv("OPENAI_TEMPERATURE", 0.0)),
        )

        self.model = OpenAIChatCompletionsModel(
            os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_client=self.openai_client,
        )
        logger.info(f"Using model: {self.model}")

        tools = [
            get_current_time,
            query_ticker_from_yahoo_finance,
        ]
        self.japanese_agent = Agent(
            name="Japanese agent",
            instructions="You only speak Japanese.",
            handoff_description="Switch to another language if user speaks another language",
            model=self.model,
            model_settings=self.model_settings,
            tools=tools,
        )

        self.english_agent = Agent(
            name="English agent",
            instructions="You only speak English",
            handoff_description="Switch to another language if user speaks another language",
            model=self.model,
            model_settings=self.model_settings,
            tools=tools,
        )

        self.taiwanese_agent = Agent(
            name="Taiwanese agent",
            instructions="You only speak Taiwanese",
            handoff_description="Switch to another language if user speaks another language",
            model=self.model,
            model_settings=self.model_settings,
            tools=tools,
        )

        self.taiwanese_agent.handoffs = [self.japanese_agent, self.english_agent]
        self.english_agent.handoffs = [self.japanese_agent, self.taiwanese_agent]
        self.japanese_agent.handoffs = [self.english_agent, self.taiwanese_agent]

        self.current_agent = self.taiwanese_agent

        # message.chat.id -> list of messages
        self.memory: dict[str, list[TResponseInputItem]] = {}

    async def handle_agent(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return

        message_text = get_message_text(update)
        if not message_text:
            return

        # Get the memory for the current chat (group or user)
        memory_key = str(update.message.chat.id)
        messages = self.memory.get(memory_key, [])

        # add the user message to the list of messages
        messages.append({"role": "user", "content": message_text})

        # send the messages to the agent
        result = await Runner.run(self.current_agent, input=messages)

        # handle new items including messages, handoffs, and tool calls
        for new_item in result.new_items:
            agent_name = new_item.agent.name
            if isinstance(new_item, MessageOutputItem):
                logger.info("{}: {}", agent_name, ItemHelpers.text_message_output(new_item))
            elif isinstance(new_item, HandoffOutputItem):
                logger.info("Handed off from {} to {}", new_item.source_agent.name, new_item.target_agent.name)
            elif isinstance(new_item, ToolCallItem):
                logger.info("{}: Calling a tool", agent_name)
            elif isinstance(new_item, ToolCallOutputItem):
                logger.info("{}: Tool call output: {}", agent_name, new_item.output)
            else:
                logger.info("{}: Skipping item: {}", agent_name, new_item.__class__.__name__)

        # update the memory
        input_items = result.to_input_list()
        if len(input_items) > self.memory_window:
            input_items = input_items[-self.memory_window :]
        self.memory[memory_key] = input_items

        # update the current agent
        self.current_agent = result.last_agent

        await update.message.reply_text(result.final_output)
