from langchain_core.messages import AIMessage
from langgraph.types import Command

from langgraph_version.fakes import ToolCallingFake
from langgraph_version.multi_agent import build_multi_agent
from langgraph_version.support_graph import build_graph


def _start(text):
    return {"messages": [("user", text)], "passages": [], "attempts": 0}


def test_technical_question_fans_out_lookups_and_answers_with_source():
    llm = ToolCallingFake(messages=iter([AIMessage(content="Hold the reset button for 10 seconds (wifi.md).")]))
    out = build_graph(llm).invoke(_start("How do I reset the wifi? The light is orange."),
                                  {"configurable": {"thread_id": "g1"}}, version="v2")
    assert out.value["route"] == "technical"
    assert len(out.value["queries"]) == 2
    assert any("wifi.md" in p for p in out.value["passages"])
    assert out.value["attempts"] == 1
    assert "wifi.md" in out.value["messages"][-1].content


def test_review_loops_until_answer_cites_a_source():
    llm = ToolCallingFake(messages=iter([
        AIMessage(content="Just restart it."),
        AIMessage(content="Hold the reset button for 10 seconds (wifi.md)."),
    ]))
    out = build_graph(llm).invoke(_start("How do I reset the wifi?"), {"configurable": {"thread_id": "g2"}}, version="v2")
    assert out.value["attempts"] == 2


def test_refund_request_interrupts_and_resumes():
    graph = build_graph(ToolCallingFake(messages=iter([])))
    cfg = {"configurable": {"thread_id": "g3"}}
    first = graph.invoke(_start("I want a refund for order NH-1001"), cfg, version="v2")
    assert first.value["route"] == "billing"
    assert first.interrupts[0].value["question"].startswith("Approve")
    done = graph.invoke(Command(resume="yes"), cfg, version="v2")
    assert "approved" in done.value["messages"][-1].content


def test_supervisor_delegates_to_technical_subagent():
    llm = ToolCallingFake(messages=iter([
        AIMessage(content="", tool_calls=[{"name": "technical_support", "args": {"request": "wifi reset"}, "id": "c1"}]),
        AIMessage(content="Hold the reset button for 10 seconds (wifi.md)."),
        AIMessage(content="Please hold the reset button for 10 seconds."),
    ]))
    result = build_multi_agent(llm).invoke({"messages": [{"role": "user", "content": "How do I reset the wifi?"}]})
    tool_texts = [m.content for m in result["messages"] if m.type == "tool"]
    assert tool_texts == ["Hold the reset button for 10 seconds (wifi.md)."]


def test_draft_handles_gemini_content_blocks():
    # Gemini 3 returns content as a list of blocks (text plus thought signature), not a plain string.
    blocks = [{"type": "text", "text": "Hold the reset button for 10 seconds (wifi.md)."}]
    llm = ToolCallingFake(messages=iter([AIMessage(content=blocks)]))
    out = build_graph(llm).invoke(_start("How do I reset the wifi?"), {"configurable": {"thread_id": "g4"}}, version="v2")
    assert out.value["attempts"] == 1
    assert out.value["messages"][-1].content == "Hold the reset button for 10 seconds (wifi.md)."


def test_subagent_result_is_plain_text_for_content_blocks():
    blocks = [{"type": "text", "text": "Hold the reset button for 10 seconds (wifi.md)."}]
    llm = ToolCallingFake(messages=iter([
        AIMessage(content="", tool_calls=[{"name": "technical_support", "args": {"request": "wifi reset"}, "id": "c1"}]),
        AIMessage(content=blocks),
        AIMessage(content="Please hold the reset button for 10 seconds."),
    ]))
    result = build_multi_agent(llm).invoke({"messages": [{"role": "user", "content": "How do I reset the wifi?"}]})
    tool_texts = [m.content for m in result["messages"] if m.type == "tool"]
    assert tool_texts == ["Hold the reset button for 10 seconds (wifi.md)."]
