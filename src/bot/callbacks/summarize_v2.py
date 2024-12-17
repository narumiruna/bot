from __future__ import annotations

from loguru import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from .. import chains
from ..loaders.v2 import URLLoader
from ..utils import parse_url
from .utils import get_message_text


async def summarize_v2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    message_text = get_message_text(update)
    if not message_text:
        return
    logger.info("message_text: {}", message_text)

    url = parse_url(message_text)
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
