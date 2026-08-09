from typing import TypedDict

class SupportAgentState(TypedDict):
    """
    Shared state passed between all LangGraph nodes.
    """
    customer_message: str
    support_policy: str
    draft_response: str
    critique: str
    approved: bool
    iteration: int
