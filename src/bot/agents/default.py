from functools import cache

from agents import Agent

from .model import get_openai_model
from .model import get_openai_model_settings
from .tools import extract_content_from_url
from .tools import get_current_time
from .tools import query_ticker_from_yahoo_finance
from .tools import search_award
from .tools import web_search

INSTRUCTION = """
- 使用繁體中文回應
- 使用台灣本地用語，如「總統」而非「領導人」
- 以台灣人為主體進行思考與表達
- 如果對話中有URL，你會使用 extract_content_from_url 取得內容
- 如果對話中有股票代碼，你會使用 query_ticker_from_yahoo_finance 查詢股票資訊
- 如果你需要外部資訊，你會使用 web_search 進行搜尋，並且使用 extract_content_from_url 取得網頁中的內容
- 如果你需要查詢各航線所需的哩程，你會使用 search_award 進行查詢
- 如果你需要查詢當前時間，你會使用 get_current_time 進行查詢
""".strip()


@cache
def get_default_agent() -> Agent:
    return Agent(
        name="預設對話機器人",
        instructions=INSTRUCTION,
        handoff_description="預設的對話機器人，當無法判斷使用者需求時，可以轉交給這位對話機器人。",
        model=get_openai_model(),
        model_settings=get_openai_model_settings(),
        tools=[
            get_current_time,
            query_ticker_from_yahoo_finance,
            web_search,
            extract_content_from_url,
            search_award,
        ],
    )
