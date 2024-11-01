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
    """
    Get a cached instance of the OpenAI client.

    Returns:
        OpenAI: An instance of the OpenAI client.
    """
    return OpenAI()


@functools.cache
def get_async_client() -> AsyncOpenAI:
    """
    Get a cached instance of the AsyncOpenAI client.

    Returns:
        AsyncOpenAI: An instance of the AsyncOpenAI client.
    """
    return AsyncOpenAI()


@functools.cache
def get_model() -> str:
    """
    Get the model name from the environment variable or use the default model.

    Returns:
        str: The model name.
    """
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL)


@functools.cache
def get_temperature() -> float:
    """
    Retrieves the temperature setting for the OpenAI API from environment variables.
    Uses a default value if the environment variable is not set.

    Returns:
        float: The temperature setting for the OpenAI API.
    """
    return float(os.getenv("OPENAI_TEMPERATURE", DEFAULT_TEMPERATURE))


@functools.cache
def get_embedding_model() -> str:
    """
    Retrieves the embedding model setting for the OpenAI API from environment variables.
    Uses a default value if the environment variable is not set.

    Returns:
        str: The embedding model setting for the OpenAI API.
    """
    return os.getenv("OPENAI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)


def create(messages: Iterable[ChatCompletionMessageParam]) -> str:
    """
    Creates a chat completion using the OpenAI API.

    Args:
        messages (Iterable[ChatCompletionMessageParam]): The messages to be sent to the OpenAI API.

    Returns:
        str: The content of the first completion choice.

    Raises:
        ValueError: If no completion choices are returned or if the completion message content is empty.
    """
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
    """
    Asynchronously creates a chat completion using the OpenAI API.

    Args:
        messages (Iterable[ChatCompletionMessageParam]): The messages to be sent to the OpenAI API.

    Returns:
        str: The content of the first completion choice.
    """
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
    """
    Parses the chat completion messages using the specified response format.

    Args:
        messages (Iterable[ChatCompletionMessageParam]): The chat completion messages to parse.
        response_format (type[T]): The type to which the response should be parsed.

    Returns:
        T: The parsed response.

    Raises:
        ValueError: If no completion choices are returned or if no completion message is parsed.
    """
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
    """
    Asynchronously parses the chat completion messages using the specified response format.

    Args:
        messages (Iterable[ChatCompletionMessageParam]): The chat completion messages to parse.
        response_format (type[T]): The type to which the response should be parsed.

    Returns:
        T: The parsed response.

    Raises:
        ValueError: If no completion choices are returned or if no completion message is parsed.
    """
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
    """
    Creates embeddings for the given text or list of texts.

    Args:
        texts (str | list[str]): The text or list of texts to create embeddings for.

    Returns:
        CreateEmbeddingResponse: The response containing the created embeddings.

    Raises:
        ValueError: If the input texts are not a string or list of strings.
    """
    if isinstance(texts, str):
        texts = [texts]

    client = get_client()
    model = get_embedding_model()

    response = client.embeddings.create(input=texts, model=model)
    return response
