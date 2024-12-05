from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def help(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    help_text = (
        "code: https://github.com/narumiruna/bot/tree/main/bot\n"
        "/help - Show this help message\n"
        "/sum - Summarize a document or URL content\n"
        "/jp - Translate text to Japanese\n"
        "/tc - Translate text to Traditional Chinese\n"
        "/en - Translate text to English\n"
        "/polish - Polish and improve text\n"
        "/echo - Echo the message\n"
        "/yt - Search YouTube\n"
        "/g - Search Google\n"
        "/recipe - Generate a recipe\n"
        "/ljp - Analyze Japanese text for JLPT study\n"
        "/yf - Query stock ticker information\n"
        "/twse - Query Taiwan stock exchange ticker\n"
        "/trip - Get travel recommendations\n"
    )

    await update.message.reply_text(help_text)
