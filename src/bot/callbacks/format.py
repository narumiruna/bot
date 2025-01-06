from __future__ import annotations

from typing import Final

from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from .. import chains
from ..loaders import URLLoader
from ..utils import create_page
from ..utils import parse_url
from .utils import get_message_text

MAX_LENGTH: Final[int] = 1_000


async def handle_format(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    message_text = get_message_text(update)
    if not message_text:
        return

    url = parse_url(message_text)
    if url:
        message_text = URLLoader().load(url)

    text = chains.format(message_text)
    logger.info("Formatted text: {}", text)

    if len(text) > MAX_LENGTH:
        text = create_page(title="Translation", html_content=text.replace("\n", "<br>"))
    await update.message.reply_text(text)
