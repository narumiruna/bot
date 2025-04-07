from __future__ import annotations

import os
from functools import cache

import logfire
from agents import ModelSettings
from agents import OpenAIChatCompletionsModel
from agents import set_tracing_disabled
from openai import AsyncAzureOpenAI
from openai import AsyncOpenAI
from openai import OpenAIError


@cache
def get_openai_model() -> OpenAIChatCompletionsModel:
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        model = OpenAIChatCompletionsModel(model_name, openai_client=AsyncAzureOpenAI())
        set_tracing_disabled(True)
        logfire.info(f"Using Azure OpenAI model: {model}")
        return model
    except OpenAIError as e:
        logfire.warning(f"Unable to create AsyncAzureOpenAI, falling back to AsyncOpenAI, error: {e}")
    model = OpenAIChatCompletionsModel(model_name, openai_client=AsyncOpenAI())
    logfire.info(f"Using OpenAI model: {model}")
    return model


@cache
def get_openai_model_settings():
    temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.0))
    return ModelSettings(
        temperature=temperature,
        tool_choice="required",
    )
