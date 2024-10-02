from __future__ import annotations

import html
import json
import os
from typing import Callable

from loguru import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler
from telegram.ext import filters

from .polish import polish
from .summarize import summarize
from .translate import translate
from .translate import translate_and_explain
from .utils import load_document_from_url
from .utils import parse_url
from .yahoo_finance import query_tickers


def get_message_text(update: Update) -> str:
    message = update.message
    if not message:
        return ""

    message_text = message.text or ""
    reply_text = message.reply_to_message.text if message.reply_to_message and message.reply_to_message.text else ""

    return f"{reply_text}\n{message_text}" if reply_text else message_text


async def log_message_(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Message Update: {}", update)


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
    try:
        doc_text = load_document_from_url(url)
    except Exception as e:
        logger.error("Failed to load URL: {}", e)
        await update.message.reply_text(f"Failed to load URL: {url}")
        return

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


def create_error_handler(developer_chat_id: int) -> Callable:
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a telegram message to notify the developer."""
        # Log the error before we do anything else, so we can see it even if something breaks.
        logger.error("Exception while handling an update: {}", context.error)

        # Build the message with some markup and additional information about what happened.
        # You might need to add some logic to deal with messages longer than the 4096 character limit.
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            "An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        )

        # Finally, send the message
        await context.bot.send_message(chat_id=developer_chat_id, text=message, parse_mode=ParseMode.HTML)

    return error_handler


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

    developer_chat_id = os.getenv("DEVELOPER_CHAT_ID")
    if developer_chat_id:
        app.add_error_handler(create_error_handler(int(developer_chat_id)))

    app.run_polling(allowed_updates=Update.ALL_TYPES)
