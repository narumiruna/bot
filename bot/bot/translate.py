from __future__ import annotations

from typing import Callable

from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from .. import tools
from .utils import get_message_text


def create_translate_callback(lang: str) -> Callable:
    async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return

        message_text = get_message_text(update)
        if not message_text:
            return

        if context.args and context.args[0] == "explain":
            text = tools.translate_and_explain(message_text, lang=lang)
            logger.info("Translated and explained text to {}: {}", lang, text)
        else:
            text = tools.translate(message_text, lang=lang)
            logger.info("Translated text to {}: {}", lang, text)

        await update.message.reply_text(text)

    return translate
