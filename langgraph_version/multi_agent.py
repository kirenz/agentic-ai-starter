"""Module 10: supervisor pattern with subagents wrapped as tools (compare: ADK sub_agents / AgentTool).

Usage: uv run python -m langgraph_version.multi_agent
"""

from langchain.agents import create_agent
from langchain.tools import tool

from helpdesk import tools
from langgraph_version.support_agent import chat_model


def build_multi_agent(llm=None):
    model = llm or chat_model()
    technical = create_agent(
        model=model,
        tools=[tools.search_manual, tools.create_ticket],
        system_prompt="Solve Nimbus Home Hub device problems with search_manual. Cite the source file.",
    )
    billing = create_agent(
        model=model,
        tools=[tools.get_order_status, tools.search_manual],
        system_prompt="Answer order, return and refund questions. Check the return policy with search_manual.",
    )

    @tool("technical_support", description="Solves device, Wi-Fi, automation and firmware problems.")
    def call_technical(request: str) -> str:
        result = technical.invoke({"messages": [{"role": "user", "content": request}]})
        return result["messages"][-1].text

    @tool("billing_support", description="Handles orders, shipping status, returns and refunds.")
    def call_billing(request: str) -> str:
        result = billing.invoke({"messages": [{"role": "user", "content": request}]})
        return result["messages"][-1].text

    return create_agent(
        model=model,
        tools=[call_technical, call_billing],
        system_prompt=(
            "You are the front desk of Nimbus support. Delegate device problems to technical_support and "
            "order or refund questions to billing_support. Pass the full customer request. "
            "Answer the customer with the specialist's result."
        ),
    )


if __name__ == "__main__":
    agent = build_multi_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": "Where is my order NH-1002?"}]})
    print(result["messages"][-1].text)
