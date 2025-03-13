from __future__ import annotations

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


async def handle_format(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    message_text = get_message_text(message)
    if not message_text:
        return

    url = parse_url(message_text)
    if url:
        message_text = await async_load_url(url)

    resp = await chains.format(message_text)
    logger.info("Formatted text: {}", resp)

    if len(resp.content) > MAX_LENGTH:
        text = create_page(title=resp.title, html_content=resp.content.replace("\n", "<br>"))
    else:
        text = resp.content

    await message.reply_text(text)
