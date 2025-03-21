from __future__ import annotations

import os

from kabigon.pdf import read_pdf_content
from kabigon.utils import read_html_content
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from .. import chains


async def summarize_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    document = message.document
    if not document:
        return

    new_file = await context.bot.get_file(document.file_id)
    file_path = await new_file.download_to_drive()

    text = None
    if file_path.suffix == ".pdf":
        text = read_pdf_content(file_path)
    elif file_path.suffix == ".html":
        text = read_html_content(file_path)

    os.remove(file_path)

    if not text:
        return

    await message.reply_text(
        await chains.format_v2(text),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
