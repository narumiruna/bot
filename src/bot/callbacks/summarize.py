from __future__ import annotations

import os

from loguru import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from .. import chains
from ..loaders import URLLoader
from ..loaders.pdf import read_pdf_content
from ..loaders.utils import read_html_content
from ..utils import parse_url
from .utils import get_message_text


async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    message_text = get_message_text(update)
    if not message_text:
        return
    logger.info("message_text: {}", message_text)

    url = parse_url(message_text)
    if not url:
        await update.message.reply_text(f"Please provide a valid URL, got: {message_text}")
        return
    logger.info("Parsed URL: {}", url)

    try:
        text = URLLoader().load(url)
    except Exception as e:
        logger.error("Failed to load URL: {}", e)
        await update.message.reply_text(f"Unable to load content from: {url}")
        return
    logger.info("Text length: {}", len(text))

    result = chains.summarize(text)

    logger.info("Summarized text: {}", result)
    await update.message.reply_text(result, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


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
        text = read_pdf_content(file_path)
    elif file_path.suffix == ".html":
        text = read_html_content(file_path)

    if text:
        summarized = chains.summarize(text)
        await update.message.reply_text(summarized, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    os.remove(file_path)
