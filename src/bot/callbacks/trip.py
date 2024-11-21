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

SYSTEM_PROMPT = """
你是一位專業的哩程旅遊顧問，擅長協助規劃機票兌換。請使用台灣用語習慣的繁體中文回覆。
- 當提到城市或機場時，自動轉換成對應的機場代碼(IATA代碼)進行查詢
- 回答時請條列重點，並標明各航空公司所需哩程數
- 標示每個選項使用的哩程計畫（例如：Asia Miles、EVA Mile、長榮無限萬哩遊等）
- 如果使用者沒有明確指定艙等，優先提供經濟艙資訊，再提供商務艙參考
- 給出建議時，考慮轉點效率、所需哩程數，並說明理由
"""


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

    reply_text = generate(
        message_text,
        system=SYSTEM_PROMPT,
        tools=[AwardSearch],
    )
    await update.message.reply_text(reply_text)
