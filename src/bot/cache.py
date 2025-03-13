import os
from functools import cache
from typing import Final

from aiocache import Cache
from loguru import logger

DEFAULT_REDIS_URL: Final[str] = "redis://localhost:6379/0"
DEFAULT_MEMORY_URL: Final[str] = "memory://"


@cache
def get_cache_from_url(namespace: str = "bot") -> Cache:
    url = os.getenv("CACHE_URL")
    if not url:
        logger.warning("No cache url provided, using {}", DEFAULT_REDIS_URL)
        return Cache.from_url(DEFAULT_REDIS_URL)
    return Cache.from_url(url, namespace=namespace)
