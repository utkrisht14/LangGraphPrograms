# In this program stop after a maximum of 3 attempts so the graph cannot loop forever.
# LangGraph supports this pattern naturally using a conditional edge with a termination condition.


from typing import TypedDict,  Literal

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()

# --------------------------------------------------
# 1. Define State
# --------------------------------------------------

class ReflectionState(TypedDict):
    question: str
    answer: str
    critique: str
    iteration : int
    is_good: bool


# --------------------------------------------------
# 2. Create Model
# --------------------------------------------------

model = ChatOpenAI(
    model = "gpt-5",
    temperature = 0
)

# --------------------------------------------------
# 3. Generate Initial Answer
# --------------------------------------------------

def generate_answer(state: ReflectionState):

    prompt = f"""
    Answer the following question clearly and simply: 
    
    Question:
    {state["question"]}
    """

    response = model.invoke(prompt)

    return {
        "answer": response.content,
        "iteration":1
    }


# --------------------------------------------------
# 4. Reflect on Current Answer
# --------------------------------------------------

def reflect_on_answer(state: ReflectionState):

    prompt = f"""
    Review the answer below 
    
    Question:
    {state["question"]}
    
    Answer:
    {state["answer"]}
    
    Check on the answer for:
    - correctness
    - completeness
    - clarity 
    - missing important information
    
    If the answer is already good enough,
    begin your response with:
    
    GOOD
    
    Otherwise, begin your answer with:
    
    IMPROVE
    
    Then explain briefly why.   
    """

    response = model.invoke(prompt)

    critique = response.content

    is_good = critique.strip().upper().startswith("GOOD")

    return {
        "critique": critique,
        "is_good": is_good,
    }


# --------------------------------------------------
# 5. Improve Answer
# --------------------------------------------------

def improve_answer(state: ReflectionState):

    prompt = f"""
    Improve the answer using the critique.
    
    Question:
    {state["question"]}
    
    Answer:
    {state["answer"]}
    
    Critique:
    {state["critique"]}
    
    Return only the improved answer. 
    """

    response = model.invoke(prompt)

    return{
        "answer": response.content,
        "iteration": state["iteration"] + 1
    }


# --------------------------------------------------
# 6. Decide What Happens After Reflection
# --------------------------------------------------

def should_continue(state: ReflectionState) -> Literal["improve", "__ind__"]:
    # Stop if the reflection agent says
    # the answer is already good
    if state["is_good"]:
        return END

    # Stop after 3 attempts
    if state["iteration"] >= 3:
        return END

    # Otherwise improve the answer
    return "improve"

# --------------------------------------------------
# 7. Build Graph
# --------------------------------------------------

builder = StateGraph(ReflectionState)

builder.add_node(
    "generate",
    generate_answer
)

builder.add_node(
    "reflect",
    reflect_on_answer
)

builder.add_node(
    "improve",
    improve_answer
)

# --------------------------------------------------
# 8. Define Graph Flow
# --------------------------------------------------

builder.add_edge(
    START,
    "generate"
)

builder.add_edge(
    "generate",
    "reflect"
)

# Conditional decision
builder.add_conditional_edges(
    "reflect",
    should_continue,
    {
        "improve": "improve",
        END: END
    }
)

#  After improving, reflect again
builder.add_edge(
    "improve",
    "reflect"
)


# --------------------------------------------------
# 9. Compile Graph
# --------------------------------------------------

graph = builder.compile()

# --------------------------------------------------
# 10. Run Graph
# --------------------------------------------------

result = graph.invoke(
    {
        "question": "Explain why the sky appears blue.",
        "answer": "",
        "critique": "",
        "iteration": 0,
        "is_good": False
    }
)


# --------------------------------------------------
# 11. Print Final Result
# --------------------------------------------------

print("\n--- FINAL ANSWER ---")
print(result["answer"])

print("\n--- FINAL CRITIQUE ---")
print(result["critique"])

print("\n--- TOTAL ATTEMPTS ---")
print(result["iteration"])