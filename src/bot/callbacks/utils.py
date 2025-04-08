from loguru import logger
from telegram import Message


def get_user_display_name(message: Message) -> str | None:
    """Get the user's display name.

    For example:
        User(first_name='なるみ', id=123456789, is_bot=False, language_code='zh-hans', username='narumi')
        -> なるみ(narumi): Hello, world!

    Args:
        message (Message): The message object

    Returns:
        str | None: The user's display name
    """
    user = message.from_user
    if not user:
        return None

    if not user.username:
        return user.first_name

    return f"{user.first_name}({user.username})"


def get_message_text(
    message: Message,
    include_reply_to_message: bool = True,
    include_user_name: bool = False,
) -> str:
    message_text = message.text or ""
    message_text = strip_command(message_text)

    if include_user_name:
        name = get_user_display_name(message)
        if name:
            message_text = f"{name}: {message_text}"

    if include_reply_to_message:
        reply_to_message = message.reply_to_message
        if reply_to_message:
            reply_to_message_text = get_message_text(
                reply_to_message,
                include_reply_to_message=False,
                include_user_name=include_user_name,
            )
            if reply_to_message_text:
                message_text = f"{reply_to_message_text}\n\n{message_text}"

    logger.info("Message text: {text}", text=message_text)
    return message_text


def strip_command(text: str) -> str:
    """Remove the command from the text.
    For example:
    Input: "/sum 1 2 3"
    Output: "1 2 3"

    Input: "hello"
    Output: "hello"
    """
    if text.startswith("/"):
        command, *args = text.split(" ", 1)
        return args[0] if args else ""
    return text


def get_message_key(message: Message) -> str:
    return f"{message.message_id}:{message.chat.id}"
