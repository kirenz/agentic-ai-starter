"""Module 10: the Nimbus assistant with LangChain's create_agent.

Usage: uv run python -m langgraph_version.support_agent
"""

from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    PIIMiddleware,
    SummarizationMiddleware,
    ToolCallLimitMiddleware,
)
from langchain.tools import ToolRuntime, tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command

from helpdesk import tools
from helpdesk.config import MODEL_ID

SYSTEM_PROMPT = (
    "You are the support assistant of Nimbus Labs. Use search_manual for product questions and answer "
    "only from the returned passages, get_order_status for orders and create_ticket when you cannot solve "
    "a problem. Use issue_refund only for refunds that follow the return policy. "
    "Store lasting customer preferences with remember_preference and look them up with recall_preference."
)


@dataclass
class CustomerContext:
    customer_id: str


@tool
def remember_preference(preference: str, runtime: ToolRuntime[CustomerContext]) -> str:
    """Store a lasting preference of the current customer, e.g. the preferred contact channel."""
    runtime.store.put(("customers", runtime.context.customer_id), "preference", {"text": preference})
    return "saved"


@tool
def recall_preference(runtime: ToolRuntime[CustomerContext]) -> str:
    """Look up the stored preference of the current customer."""
    item = runtime.store.get(("customers", runtime.context.customer_id), "preference")
    return item.value["text"] if item else "no preference stored"


def chat_model() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model=MODEL_ID, max_retries=5)


def build_agent(llm=None, *, checkpointer=None, store=None):
    model = llm or chat_model()
    return create_agent(
        model=model,
        tools=[
            tools.search_manual,
            tools.get_order_status,
            tools.create_ticket,
            tools.issue_refund,
            remember_preference,
            recall_preference,
        ],
        system_prompt=SYSTEM_PROMPT,
        context_schema=CustomerContext,
        middleware=[
            PIIMiddleware("email", strategy="redact", apply_to_input=True),
            ToolCallLimitMiddleware(tool_name="issue_refund", thread_limit=1),
            SummarizationMiddleware(model=model, trigger=("tokens", 4000), keep=("messages", 20)),
            HumanInTheLoopMiddleware(
                interrupt_on={"issue_refund": {"allowed_decisions": ["approve", "edit", "reject"]}}
            ),
        ],
        checkpointer=checkpointer or InMemorySaver(),
        store=store or InMemoryStore(),
    )


def main() -> None:
    agent = build_agent()
    ctx = CustomerContext(customer_id="c-42")
    cfg = {"configurable": {"thread_id": "demo"}}
    out = agent.invoke(
        {"messages": [{"role": "user", "content": "Order NH-1001 arrived broken, please refund 50 EUR."}]},
        cfg, context=ctx, version="v2",
    )
    if out.interrupts:
        print("Waiting for approval:", out.interrupts[0].value["action_requests"])
        out = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), cfg, context=ctx, version="v2")
    print(out.value["messages"][-1].text)
    print("State keys:", list(agent.get_state(cfg).values))


if __name__ == "__main__":
    main()
