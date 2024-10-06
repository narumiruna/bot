from __future__ import annotations

import html
import json
import os
import traceback
from typing import Callable

from loguru import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler
from telegram.ext import filters

from .loaders import load_pdf_file
from .loaders import load_url
from .polish import polish
from .summarize import summarize
from .translate import translate
from .translate import translate_and_explain
from .utils import create_page
from .utils import parse_url
from .yahoo_finance import query_tickers


def get_message_text(update: Update) -> str:
    message = update.message
    if not message:
        return ""

    message_text = message.text or ""
    reply_text = message.reply_to_message.text if message.reply_to_message and message.reply_to_message.text else ""

    return f"{reply_text}\n{message_text}" if reply_text else message_text


async def log_message_callback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Message Update: {}", update)


async def echo_callback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    text = html.escape(
        json.dumps(
            update.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
    )
    await update.message.reply_text(
        text=f"<pre>{text}</pre>",
        parse_mode=ParseMode.HTML,
    )


async def summarize_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    message_text = get_message_text(update)
    if not message_text:
        return

    # if the message is a reply to a pdf document, summarize the pdf document
    reply_to_message = update.message.reply_to_message
    if reply_to_message and reply_to_message.document:
        new_file = await context.bot.get_file(reply_to_message.document.file_id)
        file_path = await new_file.download_to_drive()
        if file_path.suffix == ".pdf":
            text = load_pdf_file(file_path)
            summarized = summarize(text)
            await update.message.reply_text(summarized)
        # delete the downloaded file
        os.remove(file_path)
        return

    url = parse_url(message_text)
    if not url:
        # if no URL is found, summarize the message text
        # TODO: simplify this logic
        summarized = summarize(message_text)
        logger.info("Summarized text: {}", summarized)
        await update.message.reply_text(summarized)
        return
    logger.info("Parsed URL: {}", url)

    text = await load_url(url)
    if not text:
        await update.message.reply_text(f"Unable to load content from: {url}")
        return
    logger.info("Text length: {}", len(text))

    summarized = summarize(text)
    logger.info("Summarized text: {}", summarized)

    await update.message.reply_text(summarized)


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


async def polish_callback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    message_text = get_message_text(update)
    if not message_text:
        return

    text = polish(message_text)
    logger.info("Polished text: {}", text)

    await update.message.reply_text(text)


async def yf_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not context.args:
        return

    text = query_tickers(context.args)
    logger.info("Tickers: {}", text)

    await update.message.reply_text(text)


async def help_callback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    help_text = (
        "code: https://github.com/narumiruna/bot/tree/main/bot\n"
        "/help - Show this help message\n"
        "/sum - Summarize a document\n"
        "/jp - Translate text to Japanese\n"
        "/tc - Translate text to Traditional Chinese\n"
        "/en - Translate text to English\n"
        "/polish - Polish text\n"
        "/echo - Echo the message\n"
    )

    await update.message.reply_text(help_text)


async def error_callback(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update: {}", context.error)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)

    html_content = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>context.error = {html.escape(str(context.error))}</pre>\n\n"
    )
    if context.error:
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
        html_content += f"<pre>Traceback (most recent call last):\n{html.escape(tb_string)}</pre>"

    page_url = create_page(title="Error", html_content=html_content)
    developer_chat_id = os.getenv("DEVELOPER_CHAT_ID", None)
    if developer_chat_id:
        await context.bot.send_message(chat_id=developer_chat_id, text=page_url)

    # if isinstance(update, Update) and update.message:
    #     await update.message.reply_text(text=message, parse_mode=ParseMode.HTML)


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
            CommandHandler("help", help_callback, filters=chat_filter),
            CommandHandler("sum", summarize_callback, filters=chat_filter),
            CommandHandler("jp", create_translate_callback("日文"), filters=chat_filter),
            CommandHandler("tc", create_translate_callback("繁體中文"), filters=chat_filter),
            CommandHandler("en", create_translate_callback("英文"), filters=chat_filter),
            CommandHandler("polish", polish_callback, filters=chat_filter),
            CommandHandler("yf", yf_callback, filters=chat_filter),
            CommandHandler("echo", echo_callback),
            MessageHandler(filters=chat_filter, callback=log_message_callback),
        ]
    )

    app.add_error_handler(error_callback)
    app.run_polling(allowed_updates=Update.ALL_TYPES)
