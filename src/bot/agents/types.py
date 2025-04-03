from typing import TypedDict

from agents.mcp import MCPServerStdioParams


class AgentParams(TypedDict):
    command: str
    help: str
    instructions: str
    mcp_servers: dict[str, MCPServerStdioParams]
