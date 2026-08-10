# Flow of the Reflexion agent:
# 1. Generate an answer.
# 2. Critique it.
# 3. Store the feedback.
# 4. Generate again using that feedback
# 5. Repeat until good enough

from typing import TypedDict, Literal

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

load_dotenv()

# --------------------------------------------------
# 1. Define the shared state
# --------------------------------------------------

class ReflexionState(TypedDict):
    question: str
    answer: str
    feedback: str
    approved: bool
    iteration: int

# --------------------------------------------------
# 2. Define structured output for the critic
# --------------------------------------------------

class CritiqueResult(BaseModel):
    approved: bool = Field(description="True if the answer is correct and complete.")
    feedback: str  = Field(description="Specific feedback for improving the answer.")


# --------------------------------------------------
# 3. Create the model
# --------------------------------------------------

llm = ChatOpenAI(model="gpt-5", temperature=0)

# Critic uses structured output because our Python
# code needs approved=True/False for routing.
critique_llm = llm.with_structured_output(CritiqueResult)

# --------------------------------------------------
# 4. Generate / improve answer
# --------------------------------------------------

def generate_answer(state: ReflexionState):
    """
    Generate the first answer or improve the previous answer
    using feedback from the critic.
    """
    if state["iteration"] == 0:

        prompt = f"""
        Answer the following question clearly and accurately: 
        
        Question:
        {state["question"]} 
        """

    else:
        prompt = f"""
        Improve your previous answer using the critic's feedback.
        
        Question:
        {state["question"]}
        
        Previous Answer:
        {state["answer"]}
        
        Critic Feedback:
        {state["feedback"]}
        
        Return only the improved answer.
        """

    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "iteration": state["iteration"] + 1
    }


# --------------------------------------------------
# 5. Critic / Reflexion node
# --------------------------------------------------

def reflect(state: ReflexionState):
    """
    Review the current answer and produce feedback.

    This is the Reflexicon step.
    """

    prompt = f"""
    You are reviewing another AI agent's answer.
    
    Question:
    {state["question"]}
    
    Answer:
    {state["answer"]}
    
    Check the answer for:
    - correctness
    - completeness
    - clarity 
    - missing important information
    - unsupported claims 
    """

    result = critique_llm.invoke(prompt)

    return {
        "approved": result.approved,
        "feedback": result.feedback
    }


# --------------------------------------------------
# 6. Decide whether to continue
# --------------------------------------------------

MAX_ATTEMPTS = 3

def should_continue(state: ReflexionState) -> Literal["generate", "__end__"]:
    """
    Stop if the critic approves the answer
    or if we have already tried 3 times.
    """

    if state["approved"]:
        return END

    if state["iteration"] >= MAX_ATTEMPTS:
        return END

    return "generate"


# --------------------------------------------------
# 7. Build the LangGraph
# --------------------------------------------------

builder = StateGraph(ReflexionState)

# Register nodes
builder.add_node("generate", generate_answer)
builder.add_node("reflect", reflect)

# ---------
# Add edges
# ---------

# Start -> Generate -> Reflect -> End
builder.add_edge(START, "generate")

# Every generated answer must be reviewed
builder.add_edge("generate", "reflect")

# Critic decides:
# approved -> END
# rejected -> Generate again
builder.add_conditional_edges(
    "reflect",
    should_continue,
    {
        "generate": "generate",
        END : END
    }
)

# --------------------------------------------------
# 8. Compile
# --------------------------------------------------

graph = builder.compile()

# --------------------------------------------------
# 9. Run
# --------------------------------------------------

result = graph.invoke(
    {
        "question":
            "Why is exercise beneficial for the human body?",
        "answer": "",
        "feedback": "",
        "approved": False,
        "iteration": 0
    }
)

# --------------------------------------------------
# 10. Show result
# --------------------------------------------------

print("\n--- FINAL ANSWER ---")
print(result["answer"])

print("\n--- LAST REFLECTION ---")
print(result["feedback"])

print("\n--- APPROVED ---")
print(result["approved"])

print("\n--- TOTAL ATTEMPTS ---")
print(result["iteration"])