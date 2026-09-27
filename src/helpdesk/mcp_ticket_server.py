"""A small MCP server that exposes the ticket system over stdio.

Run standalone: uv run python -m helpdesk.mcp_ticket_server
"""

from mcp.server.mcpserver import MCPServer

from helpdesk import tools

server = MCPServer("nimbus-tickets")


@server.tool()
def create_ticket(subject: str, description: str, priority: str = "normal") -> dict:
    """Create a Nimbus support ticket and return its id."""
    return tools.create_ticket(subject, description, priority)


if __name__ == "__main__":
    server.run(transport="stdio")
