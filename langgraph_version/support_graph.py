"""Module 10: a hand-built StateGraph (compare: ADK Workflow in module 5).

classify -> technical: plan_queries -> lookup (parallel via Send) -> draft -> review (loops back to draft)
         -> billing:   approve_refund (pauses with interrupt)

Usage: uv run python -m langgraph_version.support_graph
"""

import re
from operator import add
from typing import Annotated, Literal

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, Send, interrupt
from typing_extensions import TypedDict

from helpdesk import kb

BILLING_WORDS = {"refund", "order", "invoice", "charge", "return"}
MAX_DRAFTS = 2


class SupportState(TypedDict):
    messages: Annotated[list, add_messages]
    route: str
    queries: list[str]
    passages: Annotated[list[str], add]
    attempts: int
    answer: str


class LookupInput(TypedDict):
    query: str


def _last_user_text(state: SupportState) -> str:
    return state["messages"][-1].content


def classify(state: SupportState) -> dict:
    words = set(re.findall(r"[a-z]+", _last_user_text(state).lower()))
    return {"route": "billing" if BILLING_WORDS & words else "technical"}


def plan_queries(state: SupportState) -> dict:
    parts = [p.strip() for p in re.split(r"[.?!]", _last_user_text(state)) if p.strip()]
    return {"queries": parts[:3] or [_last_user_text(state)]}


def fan_out(state: SupportState) -> list[Send]:
    return [Send("lookup", {"query": q}) for q in state["queries"]]


def lookup(state: LookupInput) -> dict:
    return {"passages": [f"[{p.source}] {p.text}" for p in kb.search(state["query"])]}


def approve_refund(state: SupportState) -> dict:
    decision = interrupt({"question": "Approve this refund request?", "request": _last_user_text(state)})
    text = "Refund approved. The money is returned within five business days." if decision == "yes" \
        else "Refund not approved. A supervisor will contact you."
    return {"messages": [AIMessage(content=text)]}


def build_graph(llm):
    def draft(state: SupportState) -> dict:
        context = "\n".join(state["passages"]) or "No manual passages found."
        prompt = [("system", "Answer the Nimbus customer using only these manual passages and cite the "
                             f"source file in brackets, e.g. (wifi.md):\n{context}")] + state["messages"]
        return {"answer": llm.invoke(prompt).text, "attempts": state["attempts"] + 1}

    def review(state: SupportState) -> Command[Literal["draft", "__end__"]]:
        if ".md" in state["answer"] or state["attempts"] >= MAX_DRAFTS:
            return Command(update={"messages": [AIMessage(content=state["answer"])]}, goto=END)
        return Command(goto="draft")

    graph = StateGraph(SupportState)
    graph.add_node("classify", classify)
    graph.add_node("plan_queries", plan_queries)
    graph.add_node("lookup", lookup)
    graph.add_node("draft", draft)
    graph.add_node("review", review)
    graph.add_node("approve_refund", approve_refund)
    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", lambda s: s["route"],
                                {"technical": "plan_queries", "billing": "approve_refund"})
    graph.add_conditional_edges("plan_queries", fan_out, ["lookup"])
    graph.add_edge("lookup", "draft")
    graph.add_edge("draft", "review")
    graph.add_edge("approve_refund", END)
    return graph.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    from langgraph_version.support_agent import chat_model

    g = build_graph(chat_model())
    out = g.invoke({"messages": [("user", "How do I reset the wifi? The light is orange.")], "passages": [], "attempts": 0},
                   {"configurable": {"thread_id": "demo"}}, version="v2")
    print(out.value["route"], out.value["attempts"], "->", out.value["messages"][-1].text)
    print(g.get_graph().draw_mermaid())
