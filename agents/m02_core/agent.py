from google.adk import Agent

from helpdesk.config import model

root_agent = Agent(
    name="nimbus_core",
    model=model(),
    description="Support assistant that personalises answers with session state.",
    instruction=(
        "You are the support assistant of Nimbus Labs. The Nimbus Home Hub is a smart home hub "
        "that connects lights, plugs and sensors. "
        # TODO: use the optional session state keys customer_name and plan in the instruction
        "Answer briefly. If you do not know an answer, say so."
    ),
    output_key="last_answer",
)
