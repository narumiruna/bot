from __future__ import annotations

from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from .. import tools


async def query_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not context.args:
        return

    text = tools.query_tickers(context.args)
    logger.info("Tickers: {}", text)

    await update.message.reply_text(text)
