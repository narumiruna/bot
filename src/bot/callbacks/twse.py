from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def query_twse_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    # context.args
    if not context.args:
        return

    await update.message.reply_text("改用 /t <symbol1> <symbol2> ...")
