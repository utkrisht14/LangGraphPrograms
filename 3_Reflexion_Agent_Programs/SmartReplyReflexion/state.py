from typing import TypedDict

class ReflexionState(TypedDict):
    """ Shared state used by every LangGraph node. """

    customer_message: str
    company_policy: str
    default_response: str
    latest_feedback: str

    # Store feedbacks from all failed attempts
    feedback_history: list[str]

    approved: bool
    iteration: bool