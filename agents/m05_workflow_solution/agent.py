from google.adk import Agent, Event, Workflow
from google.adk.events import RequestInput
from pydantic import BaseModel

from helpdesk import orders, tools
from helpdesk.config import model


class Triage(BaseModel):
    category: str  # TECHNICAL, BILLING or OTHER
    order_id: str | None = None


classifier = Agent(
    name="classifier",
    model=model(),
    output_schema=Triage,
    instruction=(
        "Classify the customer message. category is TECHNICAL for device problems, "
        "BILLING for refunds, charges or orders, OTHER for everything else. "
        "Set order_id if the message contains an order number like NH-1001."
    ),
)

technical_agent = Agent(
    name="technical_support",
    model=model(),
    instruction="Solve the device problem using search_manual. Answer in at most five sentences.",
    tools=[tools.search_manual],
)


def route(node_input):
    triage = Triage.model_validate(node_input)
    # >>> EXERCISE: send the triage result along the route named by its category
    return Event(route=triage.category, output=triage)
    # <<< EXERCISE


def ask_approval(node_input, ctx):
    triage = Triage.model_validate(node_input)
    order = orders.get(triage.order_id or "")
    if order is None:
        yield Event(output="No valid order number found. Please provide your order number (e.g. NH-1001).")
        return
    # Keep the pending refund in session state; it survives the pause.
    ctx.state["pending_refund"] = {"order_id": triage.order_id, "amount_eur": order["total_eur"]}
    # >>> EXERCISE: pause the workflow and ask a supervisor to approve the refund
    yield RequestInput(
        message=f"Approve a refund of {order['total_eur']} EUR for {triage.order_id}? (yes/no)",
        payload=ctx.state["pending_refund"],
    )
    # <<< EXERCISE


def apply_decision(node_input, ctx):
    pending = ctx.state.get("pending_refund")
    if pending is None or str(node_input).strip().lower() != "yes":
        return Event(output="Refund not approved. A supervisor will contact the customer.")
    result = tools.issue_refund(pending["order_id"], pending["amount_eur"], "approved by supervisor")
    return Event(output=f"Refund approved: {result}")


def other(node_input):
    return Event(output="This request is outside Nimbus support. Please contact the shop directly.")


def build_workflow(classifier_node) -> Workflow:
    return Workflow(
        name="nimbus_workflow",
        edges=[
            ("START", classifier_node, route),
            (route, {"TECHNICAL": technical_agent, "BILLING": ask_approval, "OTHER": other}),
            (ask_approval, apply_decision),
        ],
    )


root_agent = build_workflow(classifier)
