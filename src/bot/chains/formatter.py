from textwrap import dedent
from typing import cast

from lazyopenai import generate
from loguru import logger
from pydantic import BaseModel


class FormatResponse(BaseModel):
    title: str
    content: str


def format(text: str, lang: str = "台灣中文") -> FormatResponse:
    prompt = f"""
    Extract and organize information from the input text, then translate it to {lang}.

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
        FormatResponse,
        generate(
            dedent(prompt),
            response_format=FormatResponse,
        ),
    )

    logger.info("Formatted response: {}", response)
    return response
