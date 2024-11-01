import functools
import os
from collections.abc import Iterable
from typing import Final
from typing import TypeVar

from openai import AsyncOpenAI
from openai import OpenAI
from openai.types import CreateEmbeddingResponse
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

DEFAULT_MODEL: Final[str] = "gpt-4o-mini"
DEFAULT_EMBEDDING_MODEL: Final[str] = "text-embedding-3-small"
DEFAULT_TEMPERATURE: Final[float] = 0.0

T = TypeVar("T", bound=BaseModel)


@functools.cache
def get_client() -> OpenAI:
    return OpenAI()


@functools.cache
def get_async_client() -> AsyncOpenAI:
    return AsyncOpenAI()


@functools.cache
def get_model() -> str:
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL)


@functools.cache
def get_temperature() -> float:
    return float(os.getenv("OPENAI_TEMPERATURE", DEFAULT_TEMPERATURE))


@functools.cache
def get_embedding_model() -> str:
    return os.getenv("OPENAI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)


def create(messages: Iterable[ChatCompletionMessageParam]) -> str:
    client = get_client()
    model = get_model()
    temperature = get_temperature()

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


async def async_create(messages: Iterable[ChatCompletionMessageParam]) -> str:
    client = get_async_client()
    model = get_model()
    temperature = get_temperature()

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


def parse(messages: Iterable[ChatCompletionMessageParam], response_format: type[T]) -> T:
    client = get_client()
    model = get_model()
    temperature = get_temperature()

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


async def async_parse(messages: Iterable[ChatCompletionMessageParam], response_format: type[T]) -> T:
    client = get_async_client()
    model = get_model()
    temperature = get_temperature()

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


def create_embeddings(texts: str | list[str]) -> CreateEmbeddingResponse:
    if isinstance(texts, str):
        texts = [texts]

    client = get_client()
    model = get_embedding_model()

    response = client.embeddings.create(input=texts, model=model)
    return response
