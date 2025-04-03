from typing import TypedDict

from agents.mcp import MCPServerStdioParams


class AgentParams(TypedDict):
    command: str
    instructions: str
    mcp_servers: dict[str, MCPServerStdioParams]
