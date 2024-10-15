import functools
import os
from pathlib import Path
from typing import TypedDict

from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_openai.chat_models import ChatOpenAI
from loguru import logger
from openai import OpenAI

MAX_CONTENT_LENGTH = 1_048_576


class Message(TypedDict):
    role: str
    content: str


@functools.cache
def get_openai_client() -> OpenAI:
    return OpenAI()


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
        max_tokens=128000,
        # max_completion_tokens=128000,
    )

    if not completion.choices:
        raise ValueError("No completion choices returned")

    content = completion.choices[0].message.content
    if not content:
        raise ValueError("No completion message content")

    return content


@functools.cache
def get_llm_from_env() -> BaseChatModel:
    model = os.getenv("MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("TEMPERATURE", 0.0))
    logger.info("language model: {}, temperature: {}", model, temperature)

    if model.startswith("gpt-"):
        return ChatOpenAI(model=model, temperature=temperature)
    elif model.startswith("gemini-"):
        return ChatGoogleGenerativeAI(model=model, temperature=temperature)
    else:
        raise ValueError("No API key found in environment variables")


def set_sqlite_llm_cache() -> None:
    database_path = Path.home() / ".cache" / ".langchain.db"
    logger.info("Using SQLite cache: {}", database_path)

    cache = SQLiteCache(database_path.as_posix())

    set_llm_cache(cache)
