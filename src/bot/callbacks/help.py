from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


class HelpCallback:
    def __init__(self, helps: list[str]) -> None:
        self.helps = helps

    async def __call__(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return

        await update.message.reply_text(
            "\n".join(self.helps),
            disable_web_page_preview=True,
        )
