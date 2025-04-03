from __future__ import annotations

from telegram import Update
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext.filters import BaseFilter


class HelpHandler(CommandHandler):
    def __init__(self, helps: list[str], command: str = "help", filters: BaseFilter | None = None) -> None:
        async def callback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
            if not update.message:
                return

            await update.message.reply_text(
                "\n".join(helps),
                disable_web_page_preview=True,
            )

        super().__init__(command=command, callback=callback, filters=filters)
