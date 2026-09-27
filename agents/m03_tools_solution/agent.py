from google.adk import Agent
from google.adk.tools import AgentTool, google_search

from helpdesk import tools
from helpdesk.config import model

# Built-in Google Search runs in its own agent and is used as a tool.
web_search_agent = Agent(
    name="web_search",
    model=model(),
    description="Searches the public web for general smart home questions not covered by the manual.",
    instruction="Answer the question using Google Search. Cite the sources you used.",
    tools=[google_search],
)

root_agent = Agent(
    name="nimbus_tools",
    model=model(),
    description="Nimbus support assistant with tools.",
    instruction=(
        "You are the support assistant of Nimbus Labs.\n"
        "- For product questions, call search_manual first and answer only from the returned passages.\n"
        "- For questions about an order, call get_order_status with the order number.\n"
        "- If the manual does not solve the problem, create a ticket with create_ticket.\n"
        "- Use web_search only for general questions that the manual cannot answer.\n"
        "Always mention the manual source file when you use a passage."
    ),
    tools=[
        tools.search_manual,
        # >>> EXERCISE: register the order status and ticket tools
        tools.get_order_status,
        tools.create_ticket,
        # <<< EXERCISE
        AgentTool(agent=web_search_agent),
    ],
)
