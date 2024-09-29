import functools
import os
from pathlib import Path

from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from langchain_core.language_models.chat_models import BaseChatModel
from loguru import logger


@functools.cache
def get_llm_from_env() -> BaseChatModel:
    if "OPENAI_API_KEY" in os.environ:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    elif "GOOGLE_API_KEY" in os.environ:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    else:
        raise ValueError("No API key found in environment variables")


def set_sqlite_llm_cache() -> None:
    database_path = Path.home() / ".cache" / ".langchain.db"
    logger.info("Using SQLite cache: {}", database_path)

    cache = SQLiteCache(database_path.as_posix())

    set_llm_cache(cache)
