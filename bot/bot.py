from __future__ import annotations

import os
from typing import Callable

from loguru import logger
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler
from telegram.ext import filters

from .polish import polish
from .summarize import summarize
from .translate import translate
from .utils import load_document
from .utils import parse_url


def get_message_text(update: Update) -> str:
    message = update.message
    if not message:
        return ""

    message_text = message.text or ""
    reply_text = message.reply_to_message.text if message.reply_to_message and message.reply_to_message.text else ""

    return f"{reply_text}\n{message_text}" if reply_text else message_text


async def log_message_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Message Update: {}", update)
    logger.info("Message Context: {}", context)


async def show_chat_id_(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    await update.message.reply_text(f"Chat ID: {update.message.chat_id}")


async def summarize_(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    message_text = get_message_text(update)
    if not message_text:
        return

    url = parse_url(message_text)
    if not url:
        logger.info("No URL found in message")
        return
    logger.info("Found URL: {}", url)

    # TODO: Handle the type of URL here, reply with a message if it cannot be processed
    doc_text = load_document(url)
    if not doc_text:
        logger.info("Failed to load URL: {}", url)
        await update.message.reply_text(f"Failed to load URL: {url}")
        return

    text = summarize(doc_text)
    logger.info("Summarized text: {}", text)

    await update.message.reply_text(text)


def create_translate_callback(lang: str) -> Callable:
    async def translate_(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return

        message_text = get_message_text(update)
        if not message_text:
            return

        text = translate(message_text, lang=lang)
        logger.info("Translated text to {}: {}", lang, text)

        await update.message.reply_text(text)

    return translate_


async def polish_(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    message_text = get_message_text(update)
    if not message_text:
        return

    text = polish(message_text)
    logger.info("Polished text: {}", text)

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
    app.add_handler(CommandHandler("sum", summarize_, filters=chat_filter))
    app.add_handler(CommandHandler("jp", create_translate_callback("日文"), filters=chat_filter))
    app.add_handler(CommandHandler("tc", create_translate_callback("繁體中文"), filters=chat_filter))
    app.add_handler(CommandHandler("en", create_translate_callback("英文"), filters=chat_filter))
    app.add_handler(CommandHandler("polish", polish_, filters=chat_filter))
    app.add_handler(CommandHandler("chat_id", show_chat_id_))
    app.add_handler(MessageHandler(filters=chat_filter, callback=log_message_))
    app.run_polling(allowed_updates=Update.ALL_TYPES)
