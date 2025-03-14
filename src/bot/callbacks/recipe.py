from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from .. import chains
from ..utils import parse_url
from .utils import async_load_url
from .utils import get_message_text


async def generate_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    if not context.args:
        return

    message_text = get_message_text(message)
    url = parse_url(message_text)
    if url:
        message_text = await async_load_url(url)
        recipe = await chains.generate_recipe(text=message_text)
        await message.reply_text(recipe)
    else:
        recipe = await chains.generate_recipe(text=message_text, fabricate=True)
        await message.reply_text(recipe)
