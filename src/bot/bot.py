from __future__ import annotations

import os

from loguru import logger
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from . import cb


def get_chat_filter() -> filters.BaseFilter:
    whitelist = os.getenv("BOT_WHITELIST")
    if not whitelist:
        logger.warning("No whitelist specified, allowing all chats")
        return filters.ALL
    else:
        chat_ids = [int(chat_id) for chat_id in whitelist.replace(" ", "").split(",")]
        return filters.Chat(chat_ids)


def run_bot() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN is not set")

    chat_filter = get_chat_filter()

    app = Application.builder().token(token).build()
    app.add_handlers(
        [
            CommandHandler("help", cb.help, filters=chat_filter),
            CommandHandler("sum", cb.summarize, filters=chat_filter),
            CommandHandler("jp", cb.create_translate_callback("日文"), filters=chat_filter),
            CommandHandler("tc", cb.create_translate_callback("繁體中文"), filters=chat_filter),
            CommandHandler("en", cb.create_translate_callback("英文"), filters=chat_filter),
            CommandHandler("polish", cb.polish, filters=chat_filter),
            CommandHandler("yf", cb.query_ticker, filters=chat_filter),
            CommandHandler("twse", cb.query_twse_ticker, filters=chat_filter),
            CommandHandler("yt", cb.search_youtube, filters=chat_filter),
            CommandHandler("g", cb.search_google, filters=chat_filter),
            CommandHandler("echo", cb.echo),
            MessageHandler(filters=chat_filter, callback=cb.summarize_document),
        ]
    )
    app.add_handler(MessageHandler(filters=chat_filter, callback=cb.log), group=1)

    app.add_error_handler(cb.error_callback)
    app.run_polling(allowed_updates=Update.ALL_TYPES)
