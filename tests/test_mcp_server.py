from google.adk.tools.mcp_tool import McpToolset

from agents.m03_mcp_solution.agent import root_agent


async def test_mcp_server_exposes_create_ticket():
    ticket_server = next(t for t in root_agent.tools if isinstance(t, McpToolset))
    tools = await ticket_server.get_tools()
    try:
        assert [t.name for t in tools] == ["create_ticket"]
    finally:
        await ticket_server.close()
