from __future__ import annotations

import os

from loguru import logger
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from . import callbacks
from .agents import MultiAgentService


def get_chat_filter() -> filters.BaseFilter:
    whitelist = os.getenv("BOT_WHITELIST")
    if not whitelist:
        logger.warning("No whitelist specified, allowing all chats")
        return filters.ALL
    else:
        chat_ids = [int(chat_id) for chat_id in whitelist.replace(" ", "").split(",")]
        return filters.Chat(chat_ids)


def get_bot_token() -> str:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN is not set")
    return token


def run_bot() -> None:
    chat_filter = get_chat_filter()

    multi_agent_service = MultiAgentService()

    app = Application.builder().token(get_bot_token()).build()
    app.add_handlers(
        [
            CommandHandler("a", multi_agent_service.handle_command, filters=chat_filter),
            CommandHandler("help", callbacks.handle_help, filters=chat_filter),
            CommandHandler("s", callbacks.summarize, filters=chat_filter),
            CommandHandler("jp", callbacks.create_translate_callback("日本語"), filters=chat_filter),
            CommandHandler("tc", callbacks.create_translate_callback("台灣話"), filters=chat_filter),
            CommandHandler("en", callbacks.create_translate_callback("English"), filters=chat_filter),
            CommandHandler("polish", callbacks.handle_polish, filters=chat_filter),
            CommandHandler("t", callbacks.query_ticker, filters=chat_filter),
            CommandHandler("yt", callbacks.search_youtube, filters=chat_filter),
            CommandHandler("recipe", callbacks.generate_recipe, filters=chat_filter),
            CommandHandler("ljp", callbacks.handle_learn_japanese, filters=chat_filter),
            CommandHandler("f", callbacks.handle_format, filters=chat_filter),
            CommandHandler("echo", callbacks.handle_echo),
            # Message handlers should be placed at the end.
            MessageHandler(filters=chat_filter & filters.REPLY, callback=multi_agent_service.handle_reply),
            MessageHandler(filters=chat_filter, callback=callbacks.summarize_document),
        ]
    )
    app.add_handler(MessageHandler(filters=chat_filter, callback=callbacks.log_message_update), group=1)

    callbacks.add_error_handler(app)
    app.run_polling(allowed_updates=Update.ALL_TYPES)
