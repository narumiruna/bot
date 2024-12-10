from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from .reply import send_reply_to_user
from .utils import get_message_text

SYSTEM_PROMPT = """
# 指引
- 使用繁體中文回應
- 使用台灣本地用語，如「總統」而非「領導人」
- 以台灣人為主體進行思考與表達
""".strip()


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    new_message = get_message_text(update, include_reply_to_message=True)
    if not new_message:
        return

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": new_message,
        },
    ]

    await send_reply_to_user(update, context, messages)
