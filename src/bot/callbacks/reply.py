from __future__ import annotations

from lazyopenai import create_chat
from telegram import Message
from telegram import Update
from telegram.ext import ContextTypes

from .utils import get_message_text


def get_key(message: Message) -> str:
    return f"{message.message_id}:{message.chat.id}"


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    new_message = get_message_text(update, include_reply_to_message=False)
    if not new_message:
        return

    reply_to_message = update.message.reply_to_message
    if not reply_to_message:
        return

    assert context.chat_data is not None

    chat = create_chat()
    key = get_key(reply_to_message)
    if key in context.chat_data:
        chat.load_messages(context.chat_data[key])
    chat.add_message(new_message)

    resp = chat.create()
    reply_message = await update.message.reply_text(resp)
    new_key = get_key(reply_message)
    context.chat_data[new_key] = chat.dump_messages()
