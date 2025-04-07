from __future__ import annotations

import logfire
from telegram import Update
from telegram.ext import ContextTypes


async def message_logging_callback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    logfire.info("Message Update: {}", update)
