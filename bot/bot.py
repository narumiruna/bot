from __future__ import annotations

import json
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
from .translate import translate_and_explain
from .utils import load_document
from .utils import parse_url
from .yahoo_finance import query_tickers


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


async def echo_message_(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    await update.message.reply_text(json.dumps(update.message.to_dict(), indent=2))


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
    async def translate_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return

        message_text = get_message_text(update)
        if not message_text:
            return

        if context.args and context.args[0] == "explain":
            text = translate_and_explain(message_text, lang=lang)
            logger.info("Translated and explained text to {}: {}", lang, text)
        else:
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


async def query_ticker_from_yahoo_finance_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not context.args:
        return

    text = query_tickers(context.args)
    logger.info("Tickers: {}", text)

    await update.message.reply_text(text)


async def help_(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    help_text = (
        "/help - Show this help message\n"
        "/sum - Summarize a document\n"
        "/jp - Translate text to Japanese\n"
        "/tc - Translate text to Traditional Chinese\n"
        "/en - Translate text to English\n"
        "/polish - Polish text\n"
        "/echo - Echo the message\n"
    )

    await update.message.reply_text(help_text)


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
            CommandHandler("help", help_, filters=chat_filter),
            CommandHandler("sum", summarize_, filters=chat_filter),
            CommandHandler("jp", create_translate_callback("日文"), filters=chat_filter),
            CommandHandler("tc", create_translate_callback("繁體中文"), filters=chat_filter),
            CommandHandler("en", create_translate_callback("英文"), filters=chat_filter),
            CommandHandler("polish", polish_, filters=chat_filter),
            CommandHandler("yf", query_ticker_from_yahoo_finance_, filters=chat_filter),
            CommandHandler("echo", echo_message_),
            MessageHandler(filters=chat_filter, callback=log_message_),
        ]
    )
    app.run_polling(allowed_updates=Update.ALL_TYPES)
