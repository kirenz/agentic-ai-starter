from google.adk import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from helpdesk import tools
from helpdesk.config import model

root_agent = Agent(
    name="nimbus_a2a_triage",
    model=model(),
    description="Front desk that delegates billing to a remote agent.",
    instruction=(
        "Solve device problems yourself with search_manual. "
        "Transfer every order or refund question to billing_service."
    ),
    tools=[tools.search_manual],
    sub_agents=[
        # TODO: connect the remote billing service through its agent card
    ],
)
