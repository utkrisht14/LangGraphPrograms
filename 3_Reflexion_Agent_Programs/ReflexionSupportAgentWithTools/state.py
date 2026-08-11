from typing import TypedDict

class AgentState(TypedDict):
    """ Shared state used by every LangGraph node. """

    question: str
    answer: str
    feedback: str
    approved: bool
    iteration: int

    