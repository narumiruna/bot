from __future__ import annotations

import os

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from .. import chains
from ..loaders import load_html_file
from ..loaders.v2.pdf import read_pdf_content
from .utils import get_message_text


async def summarize_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    document = update.message.document
    if not document:
        return

    new_file = await context.bot.get_file(document.file_id)
    file_path = await new_file.download_to_drive()

    text = None
    if file_path.suffix == ".pdf":
        text = read_pdf_content(file_path)
    elif file_path.suffix == ".html":
        text = load_html_file(file_path)

    if text:
        summarized = chains.summarize(text)
        await update.message.reply_text(summarized, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    os.remove(file_path)


async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    message_text = get_message_text(update)
    if not message_text:
        return

    await update.message.reply_text("改用 /s <url>")
