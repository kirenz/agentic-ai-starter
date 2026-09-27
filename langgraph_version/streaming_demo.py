"""Module 10: watch the agent work step by step and token by token.

Usage: uv run python -m langgraph_version.streaming_demo
"""

from langgraph_version.support_agent import CustomerContext, build_agent


def main() -> None:
    agent = build_agent()
    cfg = {"configurable": {"thread_id": "stream-demo"}}
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": "How do I reset the wifi of my hub?"}]},
        cfg,
        context=CustomerContext(customer_id="c-7"),
        stream_mode=["updates", "messages"],
        version="v2",
    ):
        if chunk["type"] == "messages":
            token, meta = chunk["data"]
            if meta["langgraph_node"] == "model":  # skip tool results, show only model tokens
                print(token.text, end="", flush=True)  # .text drops thought signatures
        elif chunk["type"] == "updates":
            print(f"\n[step] {', '.join(chunk['data'])}")


if __name__ == "__main__":
    main()
