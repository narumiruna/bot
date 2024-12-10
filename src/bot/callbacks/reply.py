from __future__ import annotations

from lazyopenai import create_chat
from telegram import Update
from telegram.ext import ContextTypes

from ..tools import GoogleSearch
from ..tools import LoanTool
from ..tools import TarotCard
from .utils import get_message_key
from .utils import get_message_text


async def send_reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE, messages) -> None:
    if not update.message:
        return

    chat = create_chat(tools=[GoogleSearch, TarotCard, LoanTool])

    chat.load_messages(messages)
    resp = chat.create()

    reply_message = await update.message.reply_text(resp)
    new_key = get_message_key(reply_message)

    context.chat_data[new_key] = chat.dump_messages()  # type: ignore


async def handle_user_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    new_message = get_message_text(update, include_reply_to_message=False)
    if not new_message:
        return

    reply_to_message = update.message.reply_to_message
    if not reply_to_message:
        return

    if reply_to_message.from_user and context.bot.id != reply_to_message.from_user.id:
        return

    if not reply_to_message.text:
        return

    key = get_message_key(reply_to_message)

    messages = context.chat_data.get(key, [])  # type: ignore
    messages += [
        {
            "role": "user",
            "content": new_message,
        }
    ]

    await send_reply_to_user(update, context, messages)
