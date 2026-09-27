import sys

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

from helpdesk import tools
from helpdesk.config import model

root_agent = Agent(
    name="nimbus_mcp",
    model=model(),
    description="Nimbus support assistant that files tickets through an MCP server.",
    instruction=(
        "You are the support assistant of Nimbus Labs. Call search_manual for product questions. "
        "If the manual does not solve the problem, create a ticket with the create_ticket tool."
    ),
    tools=[
        tools.search_manual,
        # TODO: connect the ticket MCP server over stdio
    ],
)
