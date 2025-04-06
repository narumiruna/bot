from __future__ import annotations

import html
from typing import Final

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from youtube_search import YoutubeSearch

MAX_RESULTS: Final[int] = 10


async def search_youtube_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not context.args:
        return

    result = YoutubeSearch(search_terms="_".join(context.args), max_results=MAX_RESULTS).to_dict()
    if not result:
        return

    if isinstance(result, str):
        await update.message.reply_text(result)
        return

    html_content = "\n".join(
        [f'<a href="https://youtu.be/{item["id"]}">{html.escape(item["title"])}</a>' for item in result]
    )
    await update.message.reply_text(html_content, parse_mode=ParseMode.HTML)
