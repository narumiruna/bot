import functools
import os
from typing import Any
from typing import TypeAlias
from typing import cast

from loguru import logger
from openai import AsyncOpenAI
from openai import OpenAI
from openai.types import CreateEmbeddingResponse
from openai.types.chat import ChatCompletionAssistantMessageParam
from openai.types.chat import ChatCompletionFunctionMessageParam
from openai.types.chat import ChatCompletionSystemMessageParam
from openai.types.chat import ChatCompletionToolMessageParam
from openai.types.chat import ChatCompletionUserMessageParam
from pydantic import BaseModel

MAX_CONTENT_LENGTH = 1_048_576

# Type alias for OpenAI message types
Message: TypeAlias = (
    ChatCompletionSystemMessageParam
    | ChatCompletionUserMessageParam
    | ChatCompletionAssistantMessageParam
    | ChatCompletionToolMessageParam
    | ChatCompletionFunctionMessageParam
)


class OpenAIError(Exception):
    """Base exception for OpenAI-related errors."""

    pass


@functools.cache
def get_openai_client() -> OpenAI:
    """Get or create a cached OpenAI client instance.

    Returns:
        OpenAI: A configured OpenAI client.
    """
    return OpenAI()


@functools.cache
def get_async_openai_client() -> AsyncOpenAI:
    """Get or create a cached async OpenAI client instance.

    Returns:
        AsyncOpenAI: A configured async OpenAI client.
    """
    return AsyncOpenAI()


@functools.cache
def get_openai_model() -> str:
    """Get the OpenAI model name from environment variables.

    Returns:
        str: The model name to use.
    """
    model = os.getenv("OPENAI_MODEL")
    if not model:
        logger.warning("OPENAI_MODEL not set, using gpt-4o-mini")
        return "gpt-4o-mini"
    return model


def _validate_messages(messages: list[Message]) -> None:
    """Validate the message list and truncate content if necessary.

    Args:
        messages: List of messages to validate.

    Raises:
        ValueError: If messages list is empty or contains invalid messages.
    """
    if not messages:
        raise ValueError("Messages list cannot be empty")

    for message in messages:
        message_dict = cast(dict[str, Any], message)
        if "role" not in message_dict or "content" not in message_dict:
            raise ValueError("Invalid message format")

        content = message_dict["content"]
        if not content:
            raise ValueError("Message content cannot be empty")

        # Handle different content types safely
        if isinstance(content, str):
            message_dict["content"] = content[:MAX_CONTENT_LENGTH]
        elif isinstance(content, list):
            # For content parts (text, image, etc.), only truncate text parts
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text = cast(str, part.get("text", ""))
                    part["text"] = text[:MAX_CONTENT_LENGTH]


def _validate_completion_response(completion: Any) -> str:
    """Validate the completion response and extract content.

    Args:
        completion: The completion response from OpenAI.

    Returns:
        str: The extracted content.

    Raises:
        OpenAIError: If the response is invalid or missing content.
    """
    if not completion.choices:
        raise OpenAIError("No completion choices returned")

    content = completion.choices[0].message.content
    if not content:
        raise OpenAIError("No completion message content")

    return content


def complete(messages: list[Message]) -> str:
    """Generate a completion using the OpenAI chat API.

    Args:
        messages: List of messages for the conversation.

    Returns:
        str: The generated completion text.

    Raises:
        ValueError: If the messages are invalid.
        OpenAIError: If the API request fails or returns invalid response.
    """
    try:
        _validate_messages(messages)
        client = get_openai_client()
        model = get_openai_model()
        temperature = float(os.getenv("TEMPERATURE", "0.0"))

        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )

        return _validate_completion_response(completion)
    except Exception as e:
        logger.error("Failed to generate completion: {}", str(e))
        raise


async def acomplete(messages: list[Message]) -> str:
    """Generate a completion asynchronously using the OpenAI chat API.

    Args:
        messages: List of messages for the conversation.

    Returns:
        str: The generated completion text.

    Raises:
        ValueError: If the messages are invalid.
        OpenAIError: If the API request fails or returns invalid response.
    """
    try:
        _validate_messages(messages)
        client = get_async_openai_client()
        model = get_openai_model()
        temperature = float(os.getenv("TEMPERATURE", "0.0"))

        completion = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )

        return _validate_completion_response(completion)
    except Exception as e:
        logger.error("Failed to generate async completion: {}", str(e))
        raise


def _validate_parsed_response(completion: Any) -> BaseModel:
    """Validate the parsed completion response.

    Args:
        completion: The completion response from OpenAI.

    Returns:
        BaseModel: The parsed response.

    Raises:
        OpenAIError: If the response is invalid or missing parsed content.
    """
    if not completion.choices:
        raise OpenAIError("No completion choices returned")

    parsed = completion.choices[0].message.parsed
    if not parsed:
        raise OpenAIError("No completion message parsed")

    return parsed


def parse(messages: list[Message], response_format: Any) -> BaseModel:
    """Parse a completion using the OpenAI chat API.

    Args:
        messages: List of messages for the conversation.
        response_format: The expected response format.

    Returns:
        BaseModel: The parsed response.

    Raises:
        ValueError: If the messages are invalid.
        OpenAIError: If the API request fails or returns invalid response.
    """
    try:
        _validate_messages(messages)
        client = get_openai_client()
        model = get_openai_model()
        temperature = float(os.getenv("TEMPERATURE", "0.0"))

        completion = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format=response_format,
        )

        return _validate_parsed_response(completion)
    except Exception as e:
        logger.error("Failed to parse completion: {}", str(e))
        raise


async def aparse(messages: list[Message], response_format: Any) -> BaseModel:
    """Parse a completion asynchronously using the OpenAI chat API.

    Args:
        messages: List of messages for the conversation.
        response_format: The expected response format.

    Returns:
        BaseModel: The parsed response.

    Raises:
        ValueError: If the messages are invalid.
        OpenAIError: If the API request fails or returns invalid response.
    """
    try:
        _validate_messages(messages)
        client = get_async_openai_client()
        model = get_openai_model()
        temperature = float(os.getenv("TEMPERATURE", "0.0"))

        completion = await client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format=response_format,
        )

        return _validate_parsed_response(completion)
    except Exception as e:
        logger.error("Failed to parse async completion: {}", str(e))
        raise


@functools.cache
def get_openai_embedding_model() -> str:
    """Get the OpenAI embedding model name from environment variables.

    Returns:
        str: The embedding model name to use.
    """
    model = os.getenv("OPENAI_EMBEDDING_MODEL")
    if not model:
        logger.warning("OPENAI_EMBEDDING_MODEL not set, using text-embedding-3-small")
        return "text-embedding-3-small"
    return model


def create_embeddings(texts: str | list[str]) -> CreateEmbeddingResponse:
    """Create embeddings for the given texts using the OpenAI API.

    Args:
        texts: A single text string or list of text strings to create embeddings for.

    Returns:
        CreateEmbeddingResponse: The embedding response from OpenAI.

    Raises:
        ValueError: If the input texts are invalid.
        OpenAIError: If the API request fails.
    """
    if not texts:
        raise ValueError("Texts cannot be empty")

    if isinstance(texts, str):
        texts = [texts]

    try:
        client = get_openai_client()
        model = get_openai_embedding_model()

        response = client.embeddings.create(input=texts, model=model)
        return response
    except Exception as e:
        logger.error("Failed to create embeddings: {}", str(e))
        raise
