from __future__ import annotations

from lazyopenai import create_chat
from telegram import Update
from telegram.ext import ContextTypes

from .utils import get_message_key
from .utils import get_message_text


async def send_reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE, messages) -> None:
    chat = create_chat()

    chat.load_messages(messages)
    resp = chat.create()

    reply_message = await update.message.reply_text(resp)
    new_key = get_message_key(reply_message)
    context.chat_data[new_key] = chat.dump_messages()


async def handle_user_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    new_message = get_message_text(update, include_reply_to_message=False)
    if not new_message:
        return

    reply_to_message = update.message.reply_to_message
    if not reply_to_message:
        return

    key = get_message_key(reply_to_message)

    messages = context.chat_data.get(key, [])
    messages += [
        {
            "role": "user",
            "content": new_message,
        }
    ]

    await send_reply_to_user(update, context, messages)
