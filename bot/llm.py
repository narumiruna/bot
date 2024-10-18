import functools
import os
from typing import TypedDict

from loguru import logger
from openai import AsyncOpenAI
from openai import OpenAI
from openai.types import CreateEmbeddingResponse

MAX_CONTENT_LENGTH = 1_048_576


class Message(TypedDict):
    role: str
    content: str


@functools.cache
def get_openai_client() -> OpenAI:
    return OpenAI()


@functools.cache
def get_async_openai_client() -> AsyncOpenAI:
    return AsyncOpenAI()


@functools.cache
def get_openai_model() -> str:
    model = os.getenv("OPENAI_MODEL")
    if not model:
        logger.warning("OPENAI_MODEL not set, using gpt-4o-mini")
        return "gpt-4o-mini"
    return model


def complete(messages: list[Message]) -> str:
    client = get_openai_client()
    model = get_openai_model()

    temperature = float(os.getenv("TEMPERATURE", 0.0))
    for message in messages:
        message["content"] = message["content"][:MAX_CONTENT_LENGTH]

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )

    if not completion.choices:
        raise ValueError("No completion choices returned")

    content = completion.choices[0].message.content
    if not content:
        raise ValueError("No completion message content")

    return content


async def acomplete(messages: list[Message]) -> str:
    client = get_async_openai_client()
    model = get_openai_model()

    temperature = float(os.getenv("TEMPERATURE", 0.0))
    for message in messages:
        message["content"] = message["content"][:MAX_CONTENT_LENGTH]

    completion = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )

    if not completion.choices:
        raise ValueError("No completion choices returned")

    content = completion.choices[0].message.content
    if not content:
        raise ValueError("No completion message content")

    return content


@functools.cache
def get_openai_embedding_model() -> str:
    model = os.getenv("OPENAI_EMBEDDING_MODEL")
    if not model:
        logger.warning("OPENAI_EMBEDDING_MODEL not set, using text-embedding-3-small")
        return "text-embedding-3-small"
    return model


def create_embeddings(texts: str | list[str]) -> CreateEmbeddingResponse:
    if isinstance(texts, str):
        texts = [texts]

    client = get_openai_client()
    model = get_openai_embedding_model()

    response = client.embeddings.create(input=texts, model=model)
    return response
