from __future__ import annotations

import os
from typing import Final

from kabigon.pdf import read_pdf_content
from kabigon.utils import read_html_content
from telegram import Update
from telegram.ext import ContextTypes

from .. import chains
from ..utils import create_page

MAX_LENGTH: Final[int] = 1_000


async def file_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    result = await chains.format(text)
    if len(str(result)) > MAX_LENGTH:
        text = create_page(title=result.title, html_content=str(result).replace("\n", "<br>"))
    else:
        text = str(result)

    await message.reply_text(text)
