from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from .reply import send_reply_to_user
from .utils import get_message_text


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    new_message = get_message_text(update, include_reply_to_message=True)
    if not new_message:
        return

    messages = [
        {
            "role": "user",
            "content": new_message,
        }
    ]

    await send_reply_to_user(update, context, messages)
