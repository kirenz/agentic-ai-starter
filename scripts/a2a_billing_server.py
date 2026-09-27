"""Module 6: expose the billing specialist as an A2A service on port 8001.

Usage: uv run uvicorn scripts.a2a_billing_server:a2a_app --port 8001
Agent card: http://localhost:8001/.well-known/agent-card.json
"""

from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from helpdesk import tools
from helpdesk.config import model

billing_service = Agent(
    name="billing_service",
    model=model(),
    description="Nimbus billing service: order status, returns and refunds.",
    instruction="Answer order and refund questions with get_order_status and search_manual.",
    tools=[tools.get_order_status, tools.search_manual],
)

a2a_app = to_a2a(billing_service, port=8001)
