from __future__ import annotations

from typing import Literal

from lazyopenai import generate
from lazyopenai.types import BaseTool
from loguru import logger
from pydantic import Field
from telegram import Update
from telegram.ext import ContextTypes
from tripplus import RedemptionRequest

from .utils import get_message_text


class AwardSearch(BaseTool):
    """
    Award Search Having a problem to figure out the mileage requirement for different route and program?
    The tool makes you find the answer in 3 secs like a pro.
    """

    ori: str = Field(..., description="Origin airport code")
    dst: str = Field(..., description="Destination airport code")
    cabin: Literal["y", "c", "f"] = Field(description="Cabin class, y: economy, c: business, f: first")
    type: Literal["ow", "rt"] = Field(description="Redemption type, ow: one way, rt: round trip")

    def __call__(self) -> str:
        req = RedemptionRequest(
            ori=self.ori,
            dst=self.dst,
            cabin=self.cabin,
            type=self.type,
            programs="ALL",
        )
        logger.debug("RedemptionRequest: {}", req)

        resp = req.do().model_dump_json()
        logger.debug("RedemptionResponse: {}", resp)
        return resp


async def trip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    message_text = get_message_text(update)

    reply_text = generate(message_text, tools=[AwardSearch])
    await update.message.reply_text(reply_text)
