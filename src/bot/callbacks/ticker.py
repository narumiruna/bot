from __future__ import annotations

import json

from loguru import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from twse.stock_info import get_stock_info

from ..yahoo_finance import query_tickers


async def query_ticker_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not context.args:
        return

    # Query Yahoo Finance
    try:
        yf_result = query_tickers(context.args)
    except Exception as e:
        logger.warning("Failed to get ticker for {symbols}, got error: {error}", symbols=context.args, error=e)
        yf_result = ""

    # Query TWSE
    twse_results = []
    for symbol in context.args:
        try:
            twse_results += [get_stock_info(symbol.strip()).pretty_repr()]
        except json.JSONDecodeError as e:
            logger.warning("Failed to get ticker for {symbol}, got error: {error}", symbol=symbol, error=e)
            continue

    # Combine results
    results = []
    if yf_result:
        results += [yf_result]

    for twse_result in twse_results:
        if twse_result:
            results += [twse_result]

    result = "\n\n".join(results).strip()

    if not result:
        return

    await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN_V2)
