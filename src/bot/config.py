from __future__ import annotations

from typing import TypedDict

from agents.mcp import MCPServerStdioParams


class CommandParams(TypedDict):
    command: str
    help: str
    agent: AgentParams


class AgentParams(TypedDict):
    instructions: str
    tools: list[str]
    mcp_servers: dict[str, MCPServerStdioParams]
    output_type: str | None
