from textwrap import dedent
from typing import cast

from loguru import logger
from pydantic import BaseModel

from .utils import generate


class FormattedContent(BaseModel):
    title: str
    content: str


async def format(text: str, lang: str = "台灣中文") -> FormattedContent:
    prompt = f"""
    Extract and organize information from the input text, then translate it to {lang}.
    Do not fabricate any information.

    Please return:
    1. A clear, concise title in {lang}
    2. Well-structured Markdown content in {lang} that:
       - Uses appropriate heading levels
       - Includes lists or tables when helpful
       - Maintains the core meaning and important details from the original text

    Input text:
    ```
    {text}
    ```
    """.strip()  # noqa: E501
    response = cast(
        FormattedContent,
        await generate(
            dedent(prompt),
            response_format=FormattedContent,
        ),
    )

    logger.info("Formatted response: {}", response)
    return response
