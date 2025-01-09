from __future__ import annotations

from lazyopenai import generate

from ...tools import Weblio
from .prompts import JLPT_V3


def learn_japanese(text: str) -> str:
    return str(generate(text, JLPT_V3, tools=[Weblio]))
