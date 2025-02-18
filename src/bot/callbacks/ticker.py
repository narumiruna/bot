from __future__ import annotations

import json

from loguru import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from twse.stock_info import query_stock_info

from .. import tools


async def query_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not context.args:
        return

    # Query Yahoo Finance
    try:
        yf_result = tools.query_tickers(context.args)
    except Exception as e:
        logger.info("Failed to get ticker for {}, got error: {}", context.args, e)
        yf_result = ""

    # Query TWSE
    twse_results = []
    for symbol in context.args:
        try:
            twse_results += [query_stock_info(symbol.strip()).pretty_repr()]
        except json.JSONDecodeError as e:
            logger.error("Failed to get ticker for {}, got error: {}", symbol, e)
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
