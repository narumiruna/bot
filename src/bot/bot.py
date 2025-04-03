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
from .agents import AgentService
from .config import CommandParams
from .config import load_config


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


class AgentServiceCommand:
    def __init__(self, params: CommandParams) -> None:
        self.filters = filters
        self.command = params["command"]
        self.help = params["help"]
        self.agent = AgentService([params["agent"]])

    def get_command_handler(self, filters: filters.BaseFilter) -> CommandHandler:
        return CommandHandler(command=self.command, callback=self.agent.handle_command, filters=filters)

    def get_message_handler(self, filters: filters.BaseFilter) -> MessageHandler:
        return MessageHandler(filters=filters, callback=self.agent.handle_reply)


def run_bot(config_file: Annotated[str, typer.Option("-c", "--config")] = "config/default.json") -> None:  # noqa
    chat_filter = get_chat_filter()
    commands = [AgentServiceCommand(params) for params in load_config(config_file)]

    async def connect(application: Application) -> None:
        for command in commands:
            for agent in command.agent.agents:
                for mcp_server in agent.mcp_servers:
                    await mcp_server.connect()

    async def cleanup(application: Application) -> None:
        for command in commands:
            for agent in command.agent.agents:
                for mcp_server in agent.mcp_servers:
                    await mcp_server.cleanup()

    app = Application.builder().token(get_bot_token()).post_init(connect).post_shutdown(cleanup).build()

    for command in commands:
        app.add_handler(command.get_command_handler(filters=chat_filter))

    app.add_handlers(
        [
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
        ]
    )

    # Message handlers should be placed at the end.
    for command in commands:
        app.add_handler(command.get_message_handler(filters=chat_filter & filters.REPLY))
    app.add_handler(MessageHandler(filters=chat_filter, callback=callbacks.extract_notes_from_document))

    app.add_handler(MessageHandler(filters=chat_filter, callback=callbacks.log_message_update), group=1)

    callbacks.add_error_handler(app)
    app.run_polling(allowed_updates=Update.ALL_TYPES)
