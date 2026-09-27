from google.adk import Agent
from google.adk.apps import App
from google.adk.apps.app import EventsCompactionConfig
from google.adk.tools import load_memory

from helpdesk import tools
from helpdesk.config import model

root_agent = Agent(
    name="nimbus_context",
    model=model(),
    description="Nimbus support assistant with memory and just-in-time retrieval.",
    instruction=(
        "You are the support assistant of Nimbus Labs.\n"
        "Do not rely on prior knowledge about the product. Retrieve context just in time: "
        "call search_manual with focused keywords whenever a product detail is needed.\n"
        "If the customer refers to an earlier conversation, call load_memory first."
    ),
    tools=[
        tools.search_manual,
        # TODO: give the agent access to long-term memory
    ],
)

app = App(
    name="m04_context",
    root_agent=root_agent,
    # Summarize older events every 5 turns, keep 1 turn of overlap.
    events_compaction_config=EventsCompactionConfig(compaction_interval=5, overlap_size=1),
)
