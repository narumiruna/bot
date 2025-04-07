from __future__ import annotations

from loguru import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.utils import async_load_url

from .. import chains
from ..utils import parse_url
from .utils import get_message_text


async def summarize_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    message_text = get_message_text(message)
    if not message_text:
        return
    logger.info(f"message_text: {message_text}")

    url = parse_url(message_text)
    if not url:
        await message.reply_text(f"Please provide a valid URL, got: {message_text}")
        return
    logger.info(f"Parsed URL: {url}")

    try:
        text = await async_load_url(url)
    except Exception as e:
        logger.error(f"Failed to load URL: {e}")
        await message.reply_text(f"Unable to load content from: {url}")
        return
    logger.info(f"Text length: {len(text)}")

    result = await chains.summarize(text)

    logger.info(f"Summarized text: {result}")
    await message.reply_text(result, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
