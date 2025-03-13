from __future__ import annotations

from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from .. import chains
from .utils import get_message_text


async def handle_polish(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    message_text = get_message_text(message)
    if not message_text:
        return

    text = await chains.polish(message_text)
    logger.info("Polished text: {}", text)

    await message.reply_text(text)
