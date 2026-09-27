"""Module 10: use the same MCP ticket server as the ADK agent, now from LangChain.

Usage: uv run python -m langgraph_version.mcp_agent
"""

import asyncio
import sys

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter

from helpdesk import tools
from langgraph_version.support_agent import chat_model

MCP_CONFIG = {
    "mcpServers": {
        "tickets": {"command": sys.executable, "args": ["-m", "helpdesk.mcp_ticket_server"]},
    }
}


async def list_mcp_tool_names() -> list[str]:
    async with MCPAdapter(MCP_CONFIG) as adapter:
        return [t.name for t in await adapter.list_tools()]


async def main() -> None:
    async with MCPAdapter(MCP_CONFIG) as adapter:
        mcp_tools = await adapter.list_tools()
        agent = create_agent(
            model=chat_model(),
            tools=[tools.search_manual, *mcp_tools],
            system_prompt=(
                "You are the Nimbus support assistant. Create a ticket when the manual does not help. "
                "If the customer explicitly asks for a ticket, create it with create_ticket."
            ),
        )
        question = (
            "My automations stopped running. I already checked that all devices are online "
            "and the automation is switched on. Please open a ticket."
        )
        result = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
        print(result["messages"][-1].text)


if __name__ == "__main__":
    asyncio.run(main())
