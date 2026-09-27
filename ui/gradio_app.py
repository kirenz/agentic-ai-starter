"""Module 9: a chat UI for the Nimbus triage agent.

Usage: uv run python -m ui.gradio_app
"""

import gradio as gr
from google.adk.runners import InMemoryRunner
from google.genai import types

from agents.m06_multiagent_solution.agent import root_agent

APP_NAME = "nimbus_support_ui"
runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)


async def respond(message: str, history: list, request: gr.Request) -> str:
    # One ADK session per browser session.
    session_id = request.session_hash or "local"
    service = runner.session_service
    if await service.get_session(app_name=APP_NAME, user_id=session_id, session_id=session_id) is None:
        await service.create_session(app_name=APP_NAME, user_id=session_id, session_id=session_id)

    reply = ""
    async for event in runner.run_async(
        user_id=session_id,
        session_id=session_id,
        new_message=types.Content(role="user", parts=[types.Part(text=message)]),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            reply = "".join(p.text or "" for p in event.content.parts)
    return reply or "Sorry, no answer was produced."


demo = gr.ChatInterface(
    fn=respond,
    title="Nimbus Support Assistant",
    examples=["My hub light is solid orange", "Where is my order NH-1002?"],
)

if __name__ == "__main__":
    demo.launch()
