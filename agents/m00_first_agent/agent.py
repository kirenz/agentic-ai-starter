from google.adk import Agent

from helpdesk.config import model

root_agent = Agent(
    name="nimbus_greeter",
    model=model(),
    description="Answers general questions about the Nimbus Home Hub.",
    instruction=(
        "You are the support assistant of Nimbus Labs. The Nimbus Home Hub is a smart home hub "
        "that connects lights, plugs and sensors. Answer briefly and politely. "
        "If you do not know an answer, say so instead of guessing."
    ),
)
