from __future__ import annotations

import os

from loguru import logger
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler
from telegram.ext import filters

# from ..qdrant import add_to_qdrant
from ..qdrant import query_qdrant
from .echo import echo
from .error import error_callback
from .help import help
from .polish import polish
from .summarize import summarize
from .summarize import summarize_document
from .ticker import query_ticker
from .translate import create_translate_callback
from .utils import get_message_text


async def log_update(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Message Update: {}", update)

    if not update.message:
        return

    if not update.message.text:
        return

    if "/query" in update.message.text:
        return

    # logger.info("Upserting to Qdrant: {}", update.message.text)
    # add_to_qdrant(
    #     update.message.text,
    #     chat_id=update.message.chat.id,
    #     message_id=update.message.message_id,
    # )


async def query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    message_text = get_message_text(update)
    if not message_text:
        return

    text = query_qdrant(message_text, chat_id=update.message.chat.id)
    if not text:
        text = "No results found"
    await update.message.reply_text(text)


def run_bot() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN is not set")

    whitelist = os.getenv("BOT_WHITELIST")
    if not whitelist:
        raise ValueError("BOT_WHITELIST is not set")
    chat_ids = [int(chat_id) for chat_id in whitelist.replace(" ", "").split(",")]
    chat_filter = filters.Chat(chat_ids)

    app = Application.builder().token(token).build()
    app.add_handlers(
        [
            CommandHandler("help", help, filters=chat_filter),
            CommandHandler("sum", summarize, filters=chat_filter),
            CommandHandler("jp", create_translate_callback("日文"), filters=chat_filter),
            CommandHandler("tc", create_translate_callback("繁體中文"), filters=chat_filter),
            CommandHandler("en", create_translate_callback("英文"), filters=chat_filter),
            CommandHandler("polish", polish, filters=chat_filter),
            CommandHandler("yf", query_ticker, filters=chat_filter),
            # CommandHandler("query", query, filters=chat_filter),
            # CommandHandler("prompt", generate_prompt, filters=chat_filter),
            CommandHandler("echo", echo),
            MessageHandler(filters=chat_filter, callback=summarize_document),
        ]
    )
    app.add_handler(MessageHandler(filters=chat_filter, callback=log_update), group=1)

    app.add_error_handler(error_callback)
    app.run_polling(allowed_updates=Update.ALL_TYPES)
