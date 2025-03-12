from __future__ import annotations

import os
from functools import cache
from typing import cast

from agents import set_default_openai_client
from agents import set_default_openai_key
from agents import set_tracing_disabled
from loguru import logger
from openai import AsyncAzureOpenAI
from openai import AsyncOpenAI


@cache
def get_openai_client() -> AsyncOpenAI:
    azure_api_key = os.getenv(key="AZURE_OPENAI_API_KEY")
    if azure_api_key is not None:
        logger.info("Using Azure OpenAI API")

        azure_client = AsyncAzureOpenAI(api_key=azure_api_key)
        set_default_openai_key(azure_api_key)
        set_default_openai_client(azure_client)

        # Disable tracing since Azure doesn't support it
        set_tracing_disabled(True)

        return cast(AsyncOpenAI, azure_client)

    return AsyncOpenAI()
