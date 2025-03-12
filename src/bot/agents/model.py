from __future__ import annotations

import os
from functools import cache

from agents import ModelSettings
from agents import OpenAIChatCompletionsModel

from .client import get_openai_client


@cache
def get_openai_model() -> OpenAIChatCompletionsModel:
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return OpenAIChatCompletionsModel(
        model_name,
        openai_client=get_openai_client(),
    )


@cache
def get_openai_model_settings():
    temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.0))
    return ModelSettings(temperature=temperature)
