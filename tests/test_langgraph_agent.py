from langchain_core.messages import AIMessage
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command

from helpdesk import tools
from langgraph_version.fakes import ToolCallingFake
from langgraph_version.support_agent import CustomerContext, build_agent

CTX = CustomerContext(customer_id="c-1")


def _call(name, args, call_id="call_1"):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id}])


def _tool_texts(messages):
    return [m.content for m in messages if m.type == "tool"]


def test_refund_pauses_for_approval_and_runs_after_approve():
    tools.reset_state()
    llm = ToolCallingFake(messages=iter([
        _call("issue_refund", {"order_id": "NH-1003", "amount_eur": 39.0, "reason": "broken"}),
        AIMessage(content="Your refund of 39 EUR is on its way."),
    ]))
    agent = build_agent(llm)
    cfg = {"configurable": {"thread_id": "t1"}}
    first = agent.invoke({"messages": [{"role": "user", "content": "Refund NH-1003"}]}, cfg, context=CTX, version="v2")
    assert first.interrupts[0].value["action_requests"][0]["name"] == "issue_refund"

    done = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), cfg, context=CTX, version="v2")
    assert any("refunded" in t for t in _tool_texts(done.value["messages"]))


def test_refund_rejected_does_not_run_tool():
    llm = ToolCallingFake(messages=iter([
        _call("issue_refund", {"order_id": "NH-1004", "amount_eur": 189.0, "reason": "late"}),
        AIMessage(content="A supervisor will review your request."),
    ]))
    agent = build_agent(llm)
    cfg = {"configurable": {"thread_id": "t2"}}
    agent.invoke({"messages": [{"role": "user", "content": "Refund NH-1004"}]}, cfg, context=CTX, version="v2")
    done = agent.invoke(Command(resume={"decisions": [{"type": "reject", "message": "Outside return window"}]}),
                        cfg, context=CTX, version="v2")
    assert not any("refunded" in t for t in _tool_texts(done.value["messages"]))


def test_store_keeps_preference_across_threads():
    store = InMemoryStore()
    llm = ToolCallingFake(messages=iter([
        _call("remember_preference", {"preference": "contact by email only"}),
        AIMessage(content="Noted."),
        _call("recall_preference", {}, call_id="call_2"),
        AIMessage(content="You prefer email."),
    ]))
    agent = build_agent(llm, store=store)
    agent.invoke({"messages": [{"role": "user", "content": "Only email me"}]},
                 {"configurable": {"thread_id": "monday"}}, context=CTX)
    result = agent.invoke({"messages": [{"role": "user", "content": "How do I prefer contact?"}]},
                          {"configurable": {"thread_id": "friday"}}, context=CTX)
    assert "contact by email only" in _tool_texts(result["messages"])


def test_pii_middleware_redacts_email_in_input():
    llm = ToolCallingFake(messages=iter([AIMessage(content="Thanks.")]))
    agent = build_agent(llm)
    result = agent.invoke({"messages": [{"role": "user", "content": "My email is alex@example.com"}]},
                          {"configurable": {"thread_id": "t3"}}, context=CTX)
    assert "alex@example.com" not in result["messages"][0].content


async def test_mcp_adapter_lists_ticket_tool():
    from langgraph_version.mcp_agent import list_mcp_tool_names

    names = await list_mcp_tool_names()
    assert any("create_ticket" in n for n in names)


def test_stream_v2_yields_typed_update_chunks():
    llm = ToolCallingFake(messages=iter([AIMessage(content="Hold the reset button for 10 seconds.")]))
    agent = build_agent(llm)
    chunks = list(agent.stream({"messages": [{"role": "user", "content": "wifi reset?"}]},
                               {"configurable": {"thread_id": "s1"}}, context=CTX,
                               stream_mode=["updates"], version="v2"))
    assert chunks and all(set(c) >= {"type", "ns", "data"} for c in chunks)
    assert {c["type"] for c in chunks} == {"updates"}
