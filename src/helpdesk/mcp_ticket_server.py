"""A small MCP server that exposes the ticket system over stdio.

Run standalone: uv run python -m helpdesk.mcp_ticket_server
"""

import inspect

from mcp.server.mcpserver import MCPServer

from helpdesk import tools

server = MCPServer("nimbus-tickets")


# Reuse the full docstring (incl. the allowed priority values) as the tool description.
@server.tool(description=inspect.getdoc(tools.create_ticket))
def create_ticket(subject: str, description: str, priority: str = "normal") -> dict:
    return tools.create_ticket(subject, description, priority)


if __name__ == "__main__":
    server.run(transport="stdio")
