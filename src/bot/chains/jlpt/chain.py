from __future__ import annotations

from ...tools import Weblio
from ..utils import generate
from .prompts import JLPT_V3


async def learn_japanese(text: str) -> str:
    return str(await generate(text, JLPT_V3, tools=[Weblio]))
