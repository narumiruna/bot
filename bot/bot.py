from __future__ import annotations

import os

from loguru import logger
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes

from .summary import summarize
from .utils import find_url
from .utils import load_url


class Bot:
    def __init__(self, token: str, whitelist: list[str]) -> None:
        self.app = Application.builder().token(token).build()
        self.app.add_handler(CommandHandler("sum", self.summarize_url))
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
        self.whitelist = whitelist

    @classmethod
    def from_env(cls):
        token = os.getenv("BOT_TOKEN")
        if token is None:
            raise ValueError("BOT_TOKEN is not set")

        whitelist = os.getenv("WHITELIST", "").split(",")
        if not token:
            raise ValueError("WHITELIST is not set")

        return cls(token=token, whitelist=whitelist)

    async def summarize_url(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message is None:
            return

        if update.message.text is None:
            return

        logger.info("Received message: '{}' from: {}", update.message.text, update.message.chat.full_name)

        if update.message.chat_id not in self.whitelist:
            logger.info("Chat ID {} not in whitelist", update.message.chat_id)
            return

        url = find_url(update.message.text.lstrip("/sum").strip().split(" "))
        if not url:
            logger.info("No URL found in message")
            return

        logger.info("Found URL: {}", url)

        text = load_url(url)
        logger.info("Loaded text from URL: {}", text)

        await update.message.reply_text(summarize(text))
