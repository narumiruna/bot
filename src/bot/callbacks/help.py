from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def handle_help(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    help_text = (
        "code: https://github.com/narumiruna/bot\n"
        "/help - Show this help message\n"
        "/a - An agent that can assist with various tasks"
        "/s - Summarize a document or URL content\n"
        "/jp - Translate text to Japanese\n"
        "/tc - Translate text to Traditional Chinese\n"
        "/en - Translate text to English\n"
        "/polish - Polish and improve text\n"
        "/echo - Echo the message\n"
        "/yt - Search YouTube\n"
        "/recipe - Generate a recipe\n"
        "/ljp - Learn Japanese\n"
        "/t - Query ticker from Yahoo Finance and Taiwan stock exchange\n"
        "/f - Format and normalize the document in 台灣話\n"
    )

    await update.message.reply_text(help_text, disable_web_page_preview=True)
