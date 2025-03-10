from __future__ import annotations

import httpx
from markdownify import markdownify
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ..chains import extract_keywords
from ..chains import summarize
from .utils import get_message_text


async def search_google(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    text = get_message_text(update)
    if not text:
        return

    keywords = await extract_keywords(text=text)
    if not keywords:
        return

    async with httpx.AsyncClient() as client:
        resp = await client.get(url="https://www.google.com/search", params={"q": keywords})
        resp.raise_for_status()

    summarized = await summarize(text=text + "\n" + markdownify(resp.text, strip=["a", "img"]).strip())

    res = [
        summarized,
        f"🔗 <a href='https://www.google.com/search?q={keywords}'>Google Search</a>",
        "🔍 Keywords: " + keywords,
    ]

    await update.message.reply_text("\n\n".join(res), parse_mode=ParseMode.HTML, disable_web_page_preview=True)
