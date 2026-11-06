"""
DisputeShield AI — Agent Tool Registry

Re-exports Model Context Protocol (MCP) and PayPal API tools
for LangChain agent reasoning loops.
"""

from typing import List
from langchain_core.tools import BaseTool

from services.mcp_bridge import MCPBridge, get_mcp_tools


def get_agent_tools() -> List[BaseTool]:
    """Retrieve all standard LangChain tools available to the dispute agent."""
    return get_mcp_tools()
