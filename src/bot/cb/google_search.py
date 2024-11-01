from __future__ import annotations

import httpx
from markdownify import markdownify
from telegram import Update
from telegram.ext import ContextTypes

from ..tools import summarize


async def search_google(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not context.args:
        return

    async with httpx.AsyncClient() as client:
        resp = await client.get(url="https://www.google.com/search", params={"q": " ".join(context.args)})
        resp.raise_for_status()

    summarized = await summarize(text=markdownify(resp.text, strip=["a", "img"]).strip())

    await update.message.reply_text(summarized)
