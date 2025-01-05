from __future__ import annotations

import html
import json
import os
import traceback

from loguru import logger
from telegram import Update
from telegram.ext import Application
from telegram.ext import ContextTypes

from ..utils import create_page


async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update: {}", context.error)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)

    html_content = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>context.error = {html.escape(str(context.error))}</pre>\n\n"
    )
    if context.error:
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
        html_content += f"<pre>Traceback (most recent call last):\n{html.escape(tb_string)}</pre>"

    page_url = create_page(title="Error", html_content=html_content)

    chat_id = os.getenv("DEVELOPER_CHAT_ID")
    if chat_id:
        await context.bot.send_message(chat_id=chat_id, text=page_url)


def add_error_handler(app: Application) -> None:
    developer_chat_id = os.getenv("DEVELOPER_CHAT_ID", None)
    if not developer_chat_id:
        logger.warning("No developer chat ID specified, error messages will not be sent to a developer")
        return

    app.add_error_handler(handle_error)
