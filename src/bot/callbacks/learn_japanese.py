from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from .. import chains
from ..loaders import URLLoader
from ..utils import parse_url
from .utils import get_message_text


async def learn_japanese(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    text = get_message_text(update)
    if not text:
        return

    url = parse_url(text)
    if url:
        text += "\n" + URLLoader().load(url)

    res = chains.learn_japanese(text)
    await update.message.reply_text(str(res))
