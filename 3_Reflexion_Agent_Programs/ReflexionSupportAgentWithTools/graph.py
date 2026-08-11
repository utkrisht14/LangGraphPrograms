from typing import Literal

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from state import AgentState
from nodes import generate_answer, review_answer, revise_answer
from tools import search_company_policy, get_order_status

from dotenv import load_dotenv

load_dotenv()

MAX_ATTEMPTS = 3


# ToolNode automatically executes tool calls made by the model.
tool_node = ToolNode(
    [
        search_company_policy,
        get_order_status
    ]
)


def should_continue(state: AgentState) -> Literal["revise", "__end__"]:
    """
    Decide whether the answer should be revised again.
    """

    if state["approved"]:
        return END

    if state["iteration"] >= MAX_ATTEMPTS:
        return END

    return "revise"


builder = StateGraph(AgentState)


# Main Reflexion nodes.
builder.add_node("generate", generate_answer)
builder.add_node("review", review_answer)
builder.add_node("revise", revise_answer)


# Start with generation.
builder.add_edge(START, "generate")
builder.add_edge("generate", "review")

builder.add_conditional_edges(
    "review",
    should_continue,
    {
        "revise": "revise",
        END: END
    }
)

# Review every revised answer again:
builder.add_edge("revise", "review")

graph = builder.compile()