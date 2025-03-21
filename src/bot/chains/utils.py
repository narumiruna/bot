import asyncio
import concurrent.futures

import lazyopenai
from lazyopenai.chat import BaseTool
from lazyopenai.chat import ResponseFormatT


async def generate(
    messages: str | list[str],
    system: str | None = None,
    response_format: type[ResponseFormatT] | None = None,
    tools: list[type[BaseTool]] | None = None,
):
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, lazyopenai.generate, messages, system, response_format, tools)
        return result


def chunk_on_delimiter(text: str, delimiter: str = " ", max_length: int = 100_000) -> list[str]:
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
