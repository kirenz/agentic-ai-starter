from google.adk import Agent

from helpdesk.config import model

root_agent = Agent(
    name="nimbus_core",
    model=model(),
    description="Support assistant that personalises answers with session state.",
    instruction=(
        "You are the support assistant of Nimbus Labs. "
        # >>> EXERCISE: use the optional session state keys customer_name and plan in the instruction
        "The customer's name is {customer_name?}. Their support plan is {plan?}. "
        "Address the customer by name if it is known. "
        # <<< EXERCISE
        "Answer briefly. If you do not know an answer, say so."
    ),
    output_key="last_answer",
)
