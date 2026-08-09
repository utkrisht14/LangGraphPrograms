import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from state import ReflexionState

load_dotenv()

llm = ChatOpenAI(model="gpt-5", temperature=0)

class ReviewResult(BaseModel):
    """ Structured output returned by the reviewer. """

    approved: bool = Field(description="True only if the reply is ready to send.")
    feedback: str = Field(description="Specific feedback explaining what should be improved.")


# Same base model, but constrained to return ReviewResult.
review_llm = llm.with_structured_output(ReviewResult)


def generate_response(state: ReflexionState) -> dict:
    """
    Generate the first reply or another attempt.

    On later attempts, the generator receives all feedback collected
    from previous failures. This is the Reflexion memory.
    """

    if state["feedback_history"]:
        lessons = "\n".join(
            f"- {feedback}"
            for feedback in state["feedback_history"]
        )
    else:
        lessons = "No previous feedback. This is the first attempt."

    prompt = f"""
    You are a customer-support specialist.
    Write a professional and concise reply.
    
    CUSTOMER_MESSAGE:
    {state["customer_message"]}
    
    COMPANY_POLICY:
    {state["company_policy"]}
    
    LESSONS FROM PREVIOUS ATTEMPTS:
    {"lessons"}
    
    Requirements:
    - Follow the policy exactly.
    - Answer the customer's concern.
    - Do not invent refunds, discounts, actions, or facts.
    - Clearly ask for information that is still required.
    - Use previous feedback so you do not repeat earlier mistakes.
    - Return only the reply that should be sent to the customer.
    """

    response = llm.invoke(prompt)

    return {
        "draft_response": response.content,
        "iteration": state["iteration"] + 1
    }


def review_response(state: ReflexionState) -> dict:
    """
    Review the current draft against the policy and customer request.
    If rejected, store the feedback so future attempts can learn from it.
    """

    prompt = f"""
    You are a strict quality reviewer for customer support.
    
    CUSTOMER_MESSAGE:
    {state["customer_message"]}
    
    COMPANY_POLICY:
    {state["company_policy"]}
    
    CURRENT_RESPONSE:
    {state["draft_response"]}
    
    Check:
    1. Policy compliance.
    2. Correctness.
    3. Completeness.
    4. Clear next steps.
    5. Professional tone.
    6. Unsupported promises or invented facts.
    
    Approve only if the reply is ready to send.
    Otherwise give short, concrete feedback for the next attempt.
    """

    review = review_llm.invoke(prompt)

    feedback_history = list(state["feedback_history"])

    if not review.approved:
        feedback_history.append(review.feedback)

    return {
        "approved": review.approved,
        "latest_feedback": review.feedback,
        "feedback_history": feedback_history,
    }
