from __future__ import annotations

from agents import HandoffOutputItem
from agents import ItemHelpers
from agents import MessageOutputItem
from agents import RunItem
from agents import Runner
from agents import ToolCallItem
from agents import ToolCallOutputItem
from agents import TResponseInputItem
from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from ..agents import get_default_agent
from ..agents import get_fortune_teller_agent
from .utils import get_message_text


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
    def __init__(self, memory_window: int = 100) -> None:
        self.memory_window = memory_window

        self.furtune_teller_agent = get_fortune_teller_agent()
        self.taiwanese_agent = get_default_agent()

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
        log_run_items(result.new_items)

        # update the memory
        input_items = result.to_input_list()
        if len(input_items) > self.memory_window:
            input_items = input_items[-self.memory_window :]
        self.memory[memory_key] = input_items

        # update the current agent
        self.current_agent = result.last_agent

        await update.message.reply_text(result.final_output)
