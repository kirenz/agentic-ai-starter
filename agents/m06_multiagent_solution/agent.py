from google.adk import Agent

from helpdesk import tools
from helpdesk.config import model

technical_agent = Agent(
    name="technical_support",
    model=model(),
    description="Solves device, Wi-Fi, automation and firmware problems of the Nimbus Home Hub.",
    instruction="Use search_manual to solve the problem. If it cannot be solved, create a ticket.",
    tools=[tools.search_manual, tools.create_ticket],
)

billing_agent = Agent(
    name="billing_support",
    model=model(),
    description="Handles orders, shipping status, returns and refunds.",
    instruction=(
        "Use get_order_status for order questions. Check the return policy with search_manual "
        "before promising a refund. Never issue refunds yourself; create a ticket for the billing team."
    ),
    tools=[tools.get_order_status, tools.search_manual, tools.create_ticket],
)

root_agent = Agent(
    name="nimbus_triage",
    model=model(),
    description="Front desk of Nimbus support.",
    instruction=(
        "Greet the customer and find out what they need. Transfer device problems to "
        "technical_support and order or refund questions to billing_support. "
        "Answer only greetings and general questions yourself."
    ),
    # >>> EXERCISE: register the two specialists as sub-agents
    sub_agents=[technical_agent, billing_agent],
    # <<< EXERCISE
)
