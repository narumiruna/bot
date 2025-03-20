import asyncio
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


def chunk_on_delimiter(text: str, delimiter: str = "\n", max_length: int = 200_000) -> list[str]:
    chunks = []
    current_chunk = ""
    for word in text.split(delimiter):
        if len(current_chunk) + len(word) + len(delimiter) <= max_length:
            current_chunk += word + delimiter
        else:
            chunks.append(current_chunk)
            current_chunk = word + delimiter
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


async def create_study_notes(text: str) -> str:
    prompt = dedent(f"""
    You are a researcher adept at creating concise, well-structured study notes. Your goal is to summarize the text below in a clear, step-by-step manner while maintaining accuracy and neutrality. Please adhere to the following guidelines:

    - Thoroughly read the text provided.
    - Generate study notes that organize the information in a logical structure.
    - Use neutral, factual language.
    - Do not add, infer, or fabricate any details—only use what the text explicitly states.
    - Keep the notes concise yet comprehensive.
    - Maintain a clear, step-by-step approach throughout the summary.

    Text to summarize:
    ```
    {text}
    ```
    """).strip()  # noqa
    result = await generate(prompt)
    return result


async def format_v2(text: str) -> FormattedContent:
    chunks = chunk_on_delimiter(text)

    if len(chunks) == 1:
        return await format(text)

    results = await asyncio.gather(*[create_study_notes(chunk) for chunk in chunks])
    return await format("\n".join(results))
