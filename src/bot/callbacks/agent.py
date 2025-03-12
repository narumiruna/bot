from __future__ import annotations

import os
from typing import Final

from agents import Agent
from agents import HandoffOutputItem
from agents import ItemHelpers
from agents import MessageOutputItem
from agents import ModelSettings
from agents import Runner
from agents import ToolCallItem
from agents import ToolCallOutputItem
from agents import TResponseInputItem
from agents import trace
from rich import print
from telegram import Update
from telegram.ext import ContextTypes

from .utils import get_message_text

MEMORY_WINDOW: Final[int] = 100

model_settings = ModelSettings(
    temperature=float(os.getenv("OPENAI_TEMPERATURE", 0.0)),
)
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

japanese_agent = Agent(
    name="Japanese agent",
    handoff_description="When the user speaks Japanese",
    instructions="You only speak Japanese.",
    model=model,
    model_settings=model_settings,
)

english_agent = Agent(
    name="English agent",
    handoff_description="When the user speaks English",
    instructions="You only speak English",
    model=model,
    model_settings=model_settings,
)

taiwanese_agent = Agent(
    name="Taiwanese agent",
    handoff_description="When the user speaks Taiwanese",
    instructions="You only speak Taiwanese",
    model=model,
    model_settings=model_settings,
)


triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[japanese_agent, english_agent, taiwanese_agent],
    model=model,
    model_settings=model_settings,
)


taiwanese_agent.handoffs = [japanese_agent, english_agent, triage_agent]
english_agent.handoffs = [japanese_agent, taiwanese_agent, triage_agent]
japanese_agent.handoffs = [english_agent, taiwanese_agent, triage_agent]


current_agent = triage_agent


# message.chat.id -> list of messages
memory: dict[str, list[TResponseInputItem]] = {}


async def main():
    result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
    print(result.final_output)
    # ¡Hola! Estoy bien, gracias por preguntar. ¿Y tú, cómo estás?


async def handle_agent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    message_text = get_message_text(update)
    if not message_text:
        return

    memory_key = str(update.message.chat.id)
    messages = memory.get(memory_key, [])
    messages.append({"role": "user", "content": message_text})

    global current_agent
    with trace("Telegram Bot", group_id=memory_key):
        result = await Runner.run(current_agent, input=messages)

    for new_item in result.new_items:
        agent_name = new_item.agent.name
        if isinstance(new_item, MessageOutputItem):
            (f"{agent_name}: {ItemHelpers.text_message_output(new_item)}")
        elif isinstance(new_item, HandoffOutputItem):
            await update.message.reply_text(
                f"Handed off from {new_item.source_agent.name} to {new_item.target_agent.name}"
            )
        elif isinstance(new_item, ToolCallItem):
            await update.message.reply_text(f"{agent_name}: Calling a tool")
        elif isinstance(new_item, ToolCallOutputItem):
            await update.message.reply_text(f"{agent_name}: Tool call output: {new_item.output}")
        else:
            await update.message.reply_text(f"{agent_name}: Skipping item: {new_item.__class__.__name__}")

    input_items = result.to_input_list()
    if len(input_items) > MEMORY_WINDOW:
        input_items = input_items[-MEMORY_WINDOW:]

    memory[memory_key] = input_items

    current_agent = result.last_agent

    await update.message.reply_text(result.final_output)
