"""Module 2: run an agent from Python, inspect events, state and token usage.

Usage: uv run python -m scripts.run_programmatically
"""

import asyncio

from google.adk.runners import InMemoryRunner

from agents.m02_core_solution.agent import root_agent
from helpdesk.usage import summarize

APP = "nimbus_core"


async def main() -> None:
    runner = InMemoryRunner(agent=root_agent, app_name=APP)

    # 1) Quick test without session boilerplate
    events = await runner.run_debug("What can the Nimbus Home Hub do?", quiet=True)
    print("Answer:", events[-1].content.parts[0].text)

    # 2) Explicit session with initial state
    session = await runner.session_service.create_session(
        app_name=APP, user_id="u1", session_id="s1", state={"customer_name": "Alex", "plan": "Premium"}
    )
    events = await runner.run_debug("Hi, who am I talking to?", user_id="u1", session_id=session.id, quiet=True)
    for e in events:
        print(f"[{e.author}] final={e.is_final_response()} text={e.content.parts[0].text if e.content and e.content.parts else None!r}")

    session = await runner.session_service.get_session(app_name=APP, user_id="u1", session_id="s1")
    print("State after run:", session.state)
    print("Usage:", summarize(events))


if __name__ == "__main__":
    asyncio.run(main())
