"""Module 4: remember facts across sessions with a memory service.

Usage: uv run python -m scripts.memory_demo
"""

import asyncio

from google.adk.runners import InMemoryRunner

from agents.m04_context_solution.agent import app


async def main() -> None:
    runner = InMemoryRunner(app=app)
    await runner.run_debug("My hub is order NH-1001 and it keeps losing Wi-Fi.", user_id="alex", session_id="monday", quiet=True)
    monday = await runner.session_service.get_session(app_name=app.name, user_id="alex", session_id="monday")
    await runner.memory_service.add_session_to_memory(monday)

    events = await runner.run_debug("Which order did I tell you about last time?", user_id="alex", session_id="friday", quiet=True)
    print(events[-1].content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
