from __future__ import annotations

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from twse.stock_info import query_stock_info


async def query_twse_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    # context.args
    if not context.args:
        return

    stock_info_response = query_stock_info(context.args)
    await update.message.reply_text(stock_info_response.pretty_repr(), parse_mode=ParseMode.MARKDOWN_V2)
