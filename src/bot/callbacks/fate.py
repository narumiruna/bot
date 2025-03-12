from __future__ import annotations

from agents import Runner
from telegram import Update
from telegram.ext import ContextTypes

from ..agents import get_fortune_teller_agent
from .utils import get_message_text

window_size = 100
input_items = []


async def handle_fate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    message_text = get_message_text(update)
    if not message_text:
        return

    global input_items
    input_items += [
        {
            "content": message_text,
            "role": "user",
        }
    ]

    result = await Runner.run(get_fortune_teller_agent(), input=input_items)

    input_items = result.to_input_list()
    if len(input_items) > window_size:
        input_items = input_items[-window_size:]

    await update.message.reply_text(result.final_output)
