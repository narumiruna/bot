from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        "\n".join(
            [
                "code: https://github.com/narumiruna/bot",
                "/help - Show this help message",
                "/a - An agent that can assist with various tasks",
                "/s - Summarize a document or URL content",
                "/jp - Translate text to Japanese",
                "/tc - Translate text to Traditional Chinese",
                "/en - Translate text to English",
                "/polish - Polish and improve text",
                "/echo - Echo the message",
                "/yt - Search YouTube",
                "/recipe - Generate a recipe",
                "/ljp - Learn Japanese",
                "/t - Query ticker from Yahoo Finance and Taiwan stock exchange",
                "/f - Format and normalize the document in 台灣話",
            ]
        ),
        disable_web_page_preview=True,
    )
