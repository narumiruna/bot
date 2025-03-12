from functools import cache

from agents import Agent

from .model import get_openai_model
from .model import get_openai_model_settings
from .tools import extract_content
from .tools import get_current_time
from .tools import query_ticker_from_yahoo_finance
from .tools import web_search


@cache
def get_default_agent() -> Agent:
    return Agent(
        name="預設對話機器人",
        instructions=(
            "使用繁體中文回應",
            "使用台灣本地用語，如「總統」而非「領導人」",
            "以台灣人為主體進行思考與表達",
        ),
        handoff_description="預設的對話機器人，當無法判斷使用者需求時，可以轉交給這位對話機器人。",
        model=get_openai_model(),
        model_settings=get_openai_model_settings(),
        tools=[
            get_current_time,
            query_ticker_from_yahoo_finance,
            web_search,
            extract_content,
        ],
    )
