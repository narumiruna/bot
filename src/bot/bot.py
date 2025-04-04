from __future__ import annotations

import os
from typing import Annotated

import typer
from loguru import logger
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from . import callbacks
from .callbacks import HelpHandler
from .config import load_config
from .service import AgentService


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


def run_bot(config_file: Annotated[str, typer.Option("-c", "--config")] = "config/default.json") -> None:  # noqa
    chat_filter = get_chat_filter()

    service = AgentService(load_config(config_file))

    async def connect(application: Application) -> None:
        await service.connect()

    async def cleanup(application: Application) -> None:
        await service.cleanup()

    app = Application.builder().token(get_bot_token()).post_init(connect).post_shutdown(cleanup).build()

    helps = [
        "code: https://github.com/narumiruna/bot",
        "/help - Show this help message",
        "/s - Summarize a document or URL content",
        "/jp - Translate text to Japanese",
        "/tc - Translate text to Traditional Chinese",
        "/en - Translate text to English",
        "/echo - Echo the message",
        "/yt - Search YouTube",
        "/t - Query ticker from Yahoo Finance and Taiwan stock exchange",
        "/f - Format and normalize the document in 台灣話",
    ]
    helps.append(f"/{service.command} - {service.help}")

    app.add_handler(service.get_command_handler(filters=chat_filter))
    app.add_handlers(
        [
            HelpHandler(helps=helps),
            CommandHandler("s", callbacks.summarize, filters=chat_filter),
            CommandHandler("jp", callbacks.create_translate_callback("日本語"), filters=chat_filter),
            CommandHandler("tc", callbacks.create_translate_callback("台灣話"), filters=chat_filter),
            CommandHandler("en", callbacks.create_translate_callback("English"), filters=chat_filter),
            CommandHandler("t", callbacks.query_ticker, filters=chat_filter),
            CommandHandler("yt", callbacks.search_youtube, filters=chat_filter),
            CommandHandler("f", callbacks.handle_format, filters=chat_filter),
            CommandHandler("echo", callbacks.handle_echo),
        ]
    )

    # Message handlers should be placed at the end.
    app.add_handler(service.get_message_handler(filters=chat_filter & filters.REPLY))
    app.add_handler(MessageHandler(filters=chat_filter, callback=callbacks.extract_notes_from_document))

    app.add_handler(MessageHandler(filters=chat_filter, callback=callbacks.log_message_update), group=1)

    callbacks.add_error_handler(app)
    app.run_polling(allowed_updates=Update.ALL_TYPES)
