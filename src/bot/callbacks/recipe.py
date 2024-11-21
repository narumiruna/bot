from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from .. import chains
from .utils import get_message_text


async def generate_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not context.args:
        return

    text = get_message_text(update)

    recipe = chains.generate_recipe(text=text)

    await update.message.reply_text(recipe)
