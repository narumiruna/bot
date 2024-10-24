from __future__ import annotations

import os

from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from .. import tools
from ..loaders import load_html_file
from ..loaders import load_pdf_file
from ..loaders import load_url
from ..utils import parse_url
from .utils import get_message_text


async def summarize_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    document = update.message.document
    if not document:
        return

    new_file = await context.bot.get_file(document.file_id)
    file_path = await new_file.download_to_drive()

    text = None
    if file_path.suffix == ".pdf":
        text = load_pdf_file(file_path)
    elif file_path.suffix == ".html":
        text = load_html_file(str(file_path))  # Convert Path to str

    if text:
        summarized = await tools.summarize(text)
        await update.message.reply_text(summarized)

    os.remove(file_path)


async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    message_text = get_message_text(update)
    if not message_text:
        return
    logger.info("message_text: {}", message_text)

    url = parse_url(message_text)
    if not url:
        # if no URL is found, summarize the message text
        # TODO: simplify this logic
        summarized = await tools.summarize(message_text)
        logger.info("Summarized text: {}", summarized)
        await update.message.reply_text(summarized)
        return
    logger.info("Parsed URL: {}", url)

    # remove the URL from the message text
    question = None
    if context.args:
        question = " ".join(context.args).replace(url, "").strip()

    text = await load_url(url)
    if not text:
        await update.message.reply_text(f"Unable to load content from: {url}")
        return
    logger.info("Text length: {}", len(text))

    summarized = await tools.summarize(text, question)
    logger.info("Summarized text: {}", summarized)

    await update.message.reply_text(summarized)
