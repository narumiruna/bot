from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from .. import chains
from ..utils import parse_url
from .utils import async_load_url
from .utils import get_message_text


async def handle_learn_japanese(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    text = get_message_text(message)
    if not text:
        return

    url = parse_url(text)
    if url:
        text += "\n" + await async_load_url(url)

    res = await chains.learn_japanese(text)
    await message.reply_text(str(res))
