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
    """
    Extracts and returns the text from an update message.

    If the message is a reply, it includes the text of the replied-to message
    followed by the text of the current message. If there is no message or
    text, it returns an empty string.

    Args:
        update (Update): The update object containing the message.

    Returns:
        str: The concatenated text of the replied-to message and the current message,
             or just the current message text if there is no reply, or an empty string
             if there is no message.
    """
    message = update.message
    if not message:
        return ""

    message_text = message.text or ""
    reply_text = message.reply_to_message.text if message.reply_to_message and message.reply_to_message.text else ""

    return f"{reply_text}\n{message_text}" if reply_text else message_text


async def log_message_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Logs the details of a message update and its context.

    Args:
        update (Update): The update object containing the message details.
        context (ContextTypes.DEFAULT_TYPE): The context object containing the context of the update.

    Returns:
        None
    """
    logger.info("Message Update: {}", update)
    logger.info("Message Context: {}", context)


async def show_chat_id_(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Asynchronously sends a message containing the chat ID of the incoming update.

    Args:
        update (Update): The incoming update object from the Telegram bot.
        _ (ContextTypes.DEFAULT_TYPE): The context object (not used in this function).

    Returns:
        None
    """
    if not update.message:
        return

    await update.message.reply_text(f"Chat ID: {update.message.chat_id}")


async def summarize_(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the summarization of a document from a URL provided in the message.

    This function extracts the message text from the update, parses it to find a URL,
    loads the document from the URL, summarizes the document, and replies with the
    summarized text. If any step fails, appropriate log messages are generated and
    a failure message is sent as a reply.

    Args:
        update (Update): The update object containing the message.
        _ (ContextTypes.DEFAULT_TYPE): The context object (unused).

    Returns:
        None
    """
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
    """
    Creates an asynchronous callback function for translating messages to a specified language.

    Args:
        lang (str): The target language code for translation.

    Returns:
        Callable: An asynchronous function that translates the message text in an update to the specified language
        and replies with the translated text.

    The returned function:
        - Extracts the message text from the update.
        - Translates the message text to the specified language.
        - Logs the translated text.
        - Sends the translated text as a reply to the original message.
    """

    async def translate_(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Asynchronously translates the text from an update message to a specified language and replies
        with the translated text.

        Args:
            update (Update): The update object containing the message to be translated.
            _ (ContextTypes.DEFAULT_TYPE): The context type, not used in this function.

        Returns:
            None
        """
        message_text = get_message_text(update)
        if not message_text:
            return

        text = translate(message_text, lang=lang)
        logger.info("Translated text to {}: {}", lang, text)

        await update.message.reply_text(text)

    return translate_


async def polish_(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle an update by polishing the message text and replying with the polished text.

    Args:
        update (Update): The update object containing the message to be polished.
        _ (ContextTypes.DEFAULT_TYPE): The context object (not used in this function).

    Returns:
        None
    """
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
