from __future__ import annotations

import os

from loguru import logger
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes

from .summary import summarize
from .utils import load_url
from .utils import parse_url


class Bot:
    def __init__(self, token: str, whitelist: list[int]) -> None:
        """
        Initialize the bot with a token and a whitelist of chat IDs.
        """
        self.whitelist = whitelist
        logger.info("whitelist: {}", self.whitelist)

        # Create the application and add the command handler
        self.app = Application.builder().token(token).build()
        self.app.add_handler(CommandHandler("sum", self.summarize_url))
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

    @classmethod
    def from_env(cls) -> Bot:
        """
        Create a Bot instance using environment variables for the token and whitelist.
        """
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise ValueError("BOT_TOKEN is not set")

        whitelist = os.getenv("BOT_WHITELIST")
        if not whitelist:
            raise ValueError("BOT_WHITELIST is not set")

        return cls(token=token, whitelist=[int(chat_id) for chat_id in whitelist.replace(" ", "").split(",")])

    async def summarize_url(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Summarize the URL found in the message text and reply with the summary.
        """
        if not update.message or not update.message.text:
            return

        logger.info("Received message: '{}' from chat ID: {}", update.message.text, update.message.chat_id)

        if update.message.chat_id not in self.whitelist:
            logger.info("Chat ID {} not in whitelist", update.message.chat_id)
            return

        raw_text = update.message.text
        if update.message.reply_to_message and update.message.reply_to_message.text:
            raw_text += "\n" + update.message.reply_to_message.text

        url = parse_url(raw_text)
        if not url:
            logger.info("No URL found in message")
            return

        logger.info("Found URL: {}", url)

        # TODO: Handle the type of URL here, reply with a message if it cannot be processed
        text = load_url(url)
        if not text:
            logger.info("Failed to load URL")
            await update.message.reply_text("Failed to load URL")
            return

        summarized = summarize()
        logger.info("Replying to chat ID: {} with: {}", update.message.chat_id, summarized)

        await update.message.reply_text(summarized)
