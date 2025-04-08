from __future__ import annotations

import os
from functools import cache

import logfire
from agents import ModelSettings
from agents import OpenAIChatCompletionsModel
from agents import set_tracing_disabled
from openai import AsyncAzureOpenAI
from openai import AsyncOpenAI

from .utils import logfire_is_enabled


@cache
def get_openai_client() -> AsyncOpenAI:
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if azure_api_key:
        set_tracing_disabled(True)
        return AsyncAzureOpenAI()
    return AsyncOpenAI()


@cache
def get_openai_model() -> OpenAIChatCompletionsModel:
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = get_openai_client()

    if logfire_is_enabled():
        logfire.instrument_openai(client)

    return OpenAIChatCompletionsModel(model_name, openai_client=client)


@cache
def get_openai_model_settings():
    temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.0))
    return ModelSettings(
        temperature=temperature,
        tool_choice="auto",
    )
