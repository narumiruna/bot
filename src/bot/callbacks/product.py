from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from .. import chains
from .utils import get_message_text


async def extract_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    text = get_message_text(update)

    products = await chains.extract_product(text=text)

    await update.message.reply_text(str(products))
