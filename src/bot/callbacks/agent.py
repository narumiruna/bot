from __future__ import annotations

from agents import HandoffOutputItem
from agents import ItemHelpers
from agents import MessageOutputItem
from agents import Runner
from agents import ToolCallItem
from agents import ToolCallOutputItem
from agents import TResponseInputItem
from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from ..agents import get_default_agent
from ..agents import get_fortune_teller_agent
from ..agents.tools import draw_tarot_card
from ..agents.tools import extract_content
from ..agents.tools import get_current_time
from ..agents.tools import query_ticker_from_yahoo_finance
from ..agents.tools import web_search
from .utils import get_message_text


class MultiAgentService:
    def __init__(self, memory_window: int = 100) -> None:
        self.memory_window = memory_window

        self.furtune_teller_agent = get_fortune_teller_agent()
        self.furtune_teller_agent.tools = [
            draw_tarot_card,
            get_current_time,
        ]

        self.taiwanese_agent = get_default_agent()
        self.taiwanese_agent.tools = [
            get_current_time,
            query_ticker_from_yahoo_finance,
            web_search,
            extract_content,
        ]

        self.taiwanese_agent.handoffs = [self.furtune_teller_agent]
        self.furtune_teller_agent.handoffs = [self.taiwanese_agent]

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
        if update.message.from_user:
            message_text = f"{update.message.from_user.first_name}: {message_text}"

        messages.append(
            {
                "role": "user",
                "content": message_text,
            }
        )

        # send the messages to the agent
        result = await Runner.run(self.current_agent, input=messages)

        # log the new items
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
