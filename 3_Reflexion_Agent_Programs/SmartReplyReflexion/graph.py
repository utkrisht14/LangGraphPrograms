from typing import Literal

from langgraph.graph import START, END, StateGraph

from nodes import generate_response, review_response
from state import ReflexionState


MAX_ATTEMPTS = 3


def route_after_review(
    state: ReflexionState,
) -> Literal["generate", "__end__"]:
    """Continue Reflexion or stop execution."""

    # Stop as soon as the reviewer approves the reply.
    if state["approved"]:
        return END

    # Prevent an endless generate-review loop.
    if state["iteration"] >= MAX_ATTEMPTS:
        return END

    # Try again. generate_response() will use feedback_history.
    return "generate"


builder = StateGraph(ReflexionState)

builder.add_node("generate", generate_response)
builder.add_node("review", review_response)

builder.add_edge(START, "generate")
builder.add_edge("generate", "review")

# review -> END
# or
# review -> generate -> review -> ...
builder.add_conditional_edges(
    "review",
    route_after_review,
    {
        "generate": "generate",
        END: END,
    },
)

reflexion_agent = builder.compile()
