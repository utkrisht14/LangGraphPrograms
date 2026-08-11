from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from state import AgentState
from tools import search_company_policy, get_order_status
from prompts import SYSTEM_PROMPT, REVIEW_PROMPT


# Main model used by the agent
llm = ChatOpenAI(model="gpt-5.2", temperature=0)


# Give the model access to two tools
agent_llm = llm.bind_tools(
    [
        search_company_policy,
        get_order_status
    ]
)


class ReviewResult(BaseModel):
    approved: bool = Field(description="Whether the answer is good enough.")
    feedback: str = Field(description="Feedback explaining what should be approved.")


# Review returns structured output
review_llm = llm.with_structured_output(ReviewResult)


def generate_answer(state: AgentState):
    """
    Generate the first answer to the customer question.
    """

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=state["question"])
    ]

    response = llm.invoke(messages)

    return {
        "answer": response.content,
        "iteration": 1
    }


def review_answer(state: AgentState):
    """
    Evaluate the generated answer.
    """

    review_request = f"""
   
    Customer question:
    {state["question"]}
    
    Agent answer:
    {state["answer"]}   
    """

    result = review_llm.invoke(
        [
            SystemMessage(content=REVIEW_PROMPT),
            HumanMessage(content=review_request)
        ]
    )

    return {
        "approved": result.approved,
        "feedback": result.feedback
    }



def revise_answer(state: AgentState):
    """
    Improve the previous answer using evaluator feedback.
    """

    revision_prompt = f"""
    
    Customer question:
    {state["question"]}
    
    Previous answer:
    {state["answer"]}
    
    Review Feedback:
    {state["feedback"]}
    
    Write an improved answer.
    
    You may use the available tools if necessary.
    """

    response = agent_llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=revision_prompt)
        ]
    )

    return {
        "answer": response.content,
        "iteration": state["iteration"] + 1
    }

