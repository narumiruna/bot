from __future__ import annotations

from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes


async def message_logging_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Message update: {update}, context: {context}", update=update, context=context)
