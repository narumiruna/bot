from __future__ import annotations

import os
from typing import Callable

from loguru import logger
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import filters

from .summarize import summarize
from .translate import translate
from .utils import load_document
from .utils import parse_url


def get_full_message_text(update: Update) -> str:
    """
    Extract the full text of the message and the text of the reply-to message, if any.

    Args:
        update (Update): The update object containing the message.

    Returns:
        str: The combined message text and reply text, if available.
    """
    message = update.message
    if not message:
        return ""

    message_text = message.text or ""
    reply_text = message.reply_to_message.text if message.reply_to_message and message.reply_to_message.text else ""

    return f"{message_text}\n{reply_text}" if reply_text else message_text


async def show_chat_id(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the chat ID of the current chat.
    """
    if not update.message:
        return

    await update.message.reply_text(f"Chat ID: {update.message.chat_id}")


async def summarize_url(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Summarize the URL found in the message text and reply with the summary.
    """

    logger.info(update)

    if not update.message or not update.message.text:
        return

    raw_text = get_full_message_text(update)

    url = parse_url(raw_text)
    if not url:
        logger.info("No URL found in message")
        return

    logger.info("Found URL: {}", url)

    # TODO: Handle the type of URL here, reply with a message if it cannot be processed
    text = load_document(url)
    if not text:
        logger.info("Failed to load URL")
        await update.message.reply_text("Failed to load URL")
        return

    summarized = summarize(text)
    logger.info("Replying to chat ID: {} with: {}", update.message.chat_id, summarized)

    await update.message.reply_text(summarized)


def create_translate_callback(lang: str) -> Callable:
    async def translate_lang(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info(update)

        if not update.message or not update.message.text:
            return

        raw_text = get_full_message_text(update)

        translated = translate(raw_text, lang=lang)
        logger.info("Replying to chat ID: {} with: {}", update.message.chat_id, translated)

        await update.message.reply_text(translated)

    return translate_lang


def run_bot() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN is not set")

    whitelist = os.getenv("BOT_WHITELIST")
    if not whitelist:
        raise ValueError("BOT_WHITELIST is not set")
    chat_ids = [int(chat_id) for chat_id in whitelist.replace(" ", "").split(",")]

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("sum", summarize_url, filters=filters.Chat(chat_ids)))
    app.add_handler(CommandHandler("jp", create_translate_callback("日文"), filters=filters.Chat(chat_ids)))
    app.add_handler(CommandHandler("tc", create_translate_callback("繁體中文"), filters=filters.Chat(chat_ids)))
    app.add_handler(CommandHandler("en", create_translate_callback("英文"), filters=filters.Chat(chat_ids)))
    app.add_handler(CommandHandler("chat_id", show_chat_id))
    app.run_polling(allowed_updates=Update.ALL_TYPES)
