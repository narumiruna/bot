from __future__ import annotations

import html
import json

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


async def echo(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    text = html.escape(
        json.dumps(
            update.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
    )
    await update.message.reply_text(
        text=f"<pre>{text}</pre>",
        parse_mode=ParseMode.HTML,
    )
