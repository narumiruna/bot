from typing import TypedDict

from agents.mcp import MCPServerStdioParams


class AgentParams(TypedDict):
    command: str
    help: str
    instructions: str
    tools: list[str]
    mcp_servers: dict[str, MCPServerStdioParams]
    output_type: str | None
