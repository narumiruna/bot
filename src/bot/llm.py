import functools
import os
from collections.abc import Iterable
from typing import Final

from loguru import logger
from openai import AsyncOpenAI
from openai import OpenAI
from openai.types import CreateEmbeddingResponse
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

MAX_CONTENT_LENGTH: Final[int] = 1_048_576


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


def complete(messages: Iterable[ChatCompletionMessageParam]) -> str:
    client = get_openai_client()
    model = get_openai_model()

    temperature = float(os.getenv("TEMPERATURE", 0.0))

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


async def acomplete(messages: Iterable[ChatCompletionMessageParam]) -> str:
    client = get_async_openai_client()
    model = get_openai_model()

    temperature = float(os.getenv("TEMPERATURE", 0.0))

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


def parse(messages: Iterable[ChatCompletionMessageParam], response_format) -> BaseModel:
    client = get_openai_client()
    model = get_openai_model()

    temperature = float(os.getenv("TEMPERATURE", 0.0))

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        temperature=temperature,
        response_format=response_format,
    )

    if not completion.choices:
        raise ValueError("No completion choices returned")

    parsed = completion.choices[0].message.parsed
    if not parsed:
        raise ValueError("No completion message parsed")

    return parsed


async def aparse(messages: Iterable[ChatCompletionMessageParam], response_format) -> BaseModel:
    client = get_async_openai_client()
    model = get_openai_model()

    temperature = float(os.getenv("TEMPERATURE", 0.0))

    completion = await client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        temperature=temperature,
        response_format=response_format,
    )

    if not completion.choices:
        raise ValueError("No completion choices returned")

    parsed = completion.choices[0].message.parsed
    if not parsed:
        raise ValueError("No completion message parsed")

    return parsed


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
