from __future__ import annotations

from collections.abc import Callable
from typing import Final

from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from .. import chains
from ..utils import create_page
from ..utils import parse_url
from .utils import async_load_url
from .utils import get_message_text

MAX_LENGTH: Final[int] = 1_000


def create_translate_callback(lang: str) -> Callable:
    async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return

        message_text = get_message_text(update)
        if not message_text:
            return

        url = parse_url(message_text)
        if url:
            message_text = await async_load_url(url)

        if context.args and context.args[0] == "explain":
            reply_text = chains.translate_and_explain(message_text, lang=lang)
            logger.info("Translated and explained text to {}: {}", lang, reply_text)
        else:
            reply_text = chains.translate(message_text, lang=lang)
            logger.info("Translated text to {}: {}", lang, reply_text)

        if len(reply_text) > MAX_LENGTH:
            reply_text = create_page(title="Translation", html_content=reply_text.replace("\n", "<br>"))
        await update.message.reply_text(reply_text)

    return translate
