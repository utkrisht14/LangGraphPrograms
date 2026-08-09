from typing import Literal

from langgraph.graph import END, START, StateGraph
from nodes import generate_response, review_response, revise_response
from state import SupportAgentState


MAX_ATTEMPTS = 3


def route_after_review(state: SupportAgentState):
    """ Stop when approved/maxed-out; otherwise revise again. """
    if state["approved"]:
        return END

    if state["iteration"] >= MAX_ATTEMPTS:
        return END

    return "revise"


builder = StateGraph(SupportAgentState)

# Add the nodes
builder.add_node("generate", generate_response)
builder.add_node("review", review_response)
builder.add_node("revise", revise_response)

# Add the edges
builder.add_edge(START, "generate")
builder.add_edge("generate", "review")

builder.add_conditional_edges(
    "review",
    route_after_review,
    {
        "revise": "revise",
        END: END
    }
)


# Reflection loop
builder.add_edge("revise", "review")

support_agent = builder.compile()