import os

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from state import SupportAgentState

llm = ChatOpenAI(name="gpt-5", temperature=0)


class ReviewResult(BaseModel):
    """ Structured result returned by the reflection node. """

    approved: bool = Field(description="True only if the draft is ready to send to the customer.")

    fallback: bool = Field(description="Short, actionable feedback explaining what should be improved.")


review_llm = llm.with_structured_output(ReviewResult)


def generate_response(state: SupportAgentState) -> dict:
    """ Create the first customer-support response."""

    prompt = f"""
    You are a customer support agent.
    
    Write a professional, concise, and helpful reply to the answer.
    
    SUPPORT POLICY:
    {state["support_policy"]}
    
    CUSTOMER MESSAGE:
    {state["customer_message"]}
    
    Requirements:
    - Follow the support policy exactly.
    - Do not promise anything that policy doesn't allow.
    - Answer the customer's actual concern. 
    - Be polite and easy to understand.
    - Return only the reply that would be sent to customer. 
    """

    response = llm.invoke(prompt)

    return {
        "draft_response": response.content,
        "iteration": 1,
    }


def review_response(state: SupportAgentState) -> dict:
    """ Review the current draft against the policy and customer request. """
    prompt = f"""
    
    You are a strict quality reviewer for a customer-support team.
    
    Review the proposed response.
    
    CUSTOMER_MESSAGE:
    {state["customer_message"]}
    
    SUPPORT_POLICY:
    {state["support_policy"]}
    
    PROPOSED_RESPONSE:
    {state["draft_response"]}
     
    Approve the response only if it:
    1. Correctly follows the support policy.
    2. Addresses the customer's request.
    3. Does not invent facts, refunds, discounts, or promises.
    4. Is professional and clear.
    5. Does not omit an important action the customer must take.
    
    If it is not ready, provide short and specific feedback that another
    writer can use to improve it.
    """

    review = llm.invoke(prompt)

    return {
        "approved": review.approveed,
        "critique": review.feedback
    }


def revise_response(state: SupportAgentState) -> dict:
    """ Rewrite the current response using the reviewer feedback. """

    prompt = f"""
    You are revising a customer-support response.
    
    CUSTOMER_MESSAGE:
    {state["customer_message"]}
    
    SUPPORT_POLICY:
    {state["support_policy"]}
    
    CURRENT_RESPONSE:
    {state["draft_response"]}
    
    REVIEW_FEEDBACK:
    {state["critique"]}
    
    Rewrite the response so that it fixes the reviewer's concerns.

    Requirements:
    - Follow the policy exactly.
    - Do not invent information.
    - Keep the response professional and concise.
    - Return only the improved customer response.
    """

    response = llm.invoke(prompt)

    return {
        "draft_response": response.content,
        "iteration": state["iteration"] + 1
    }

