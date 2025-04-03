from functools import cache

from agents import Agent
from agents.mcp import MCPServerStdio

from .model import get_openai_model
from .model import get_openai_model_settings
from .tools import extract_content_from_url
from .tools import get_current_time
from .tools import search_award
from .tools import web_search


@cache
def get_default_agent() -> Agent:
    return Agent(
        name="Agent",
        instructions="使用台灣正體中文。擅長邏輯思考且嚴謹，會分解問題並且一步一步地思考。在寫程式時會使用英文。",
        handoff_description="預設的對話機器人，當無法判斷使用者需求時，可以轉交給這位對話機器人。",
        model=get_openai_model(),
        model_settings=get_openai_model_settings(),
        tools=[
            get_current_time,
            web_search,
            extract_content_from_url,
            search_award,
        ],
        mcp_servers=[
            MCPServerStdio(
                params={
                    "command": "/Users/narumi/.cargo/bin/uv",
                    "args": ["yfmcp"],
                }
            ),
            # https://github.com/modelcontextprotocol/servers/tree/main/src/time
            MCPServerStdio(
                params={
                    "command": "/Users/narumi/.cargo/bin/uv",
                    "args": ["mcp-server-time", "--local-timezone=Asia/Taipei"],
                }
            ),
        ],
    )
