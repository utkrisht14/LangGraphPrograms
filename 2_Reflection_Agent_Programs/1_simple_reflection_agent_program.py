from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()

# --------------------------------------------------
# 1. Define the State
# --------------------------------------------------

class ReflectionState(TypedDict):
    question:str
    answer:str
    critique:str
    final_answer:str


# --------------------------------------------------
# 2. Initialize the model
# --------------------------------------------------

model = ChatOpenAI(
    model="gpt-5",
    temperature=0
)

# --------------------------------------------------
# 3. Generator Node
# --------------------------------------------------

def generate_answer(state:ReflectionState):

    prompt = f"""
    Answer the following question clearly and simply: 
    
    Question:
    {state["question"]}
    """

    response = model.invoke(prompt)

    return {
        "answer": response.content
    }

# --------------------------------------------------
# 4. Reflection Node
# --------------------------------------------------

def reflect_on_answer(state: ReflectionState):
    prompt = f"""
    Review the answer below 
    
    Question:
    {state["question"]}
    
    Answer:
    {state["answer"]}
    
    Identify:
    - mistakes
    - missing information 
    - unclear explanation 
    
    Give a short critique.
    """

    response = model.invoke(prompt)

    return {
        "critique": response.content
    }

# --------------------------------------------------
# 5. Improvement Node
# --------------------------------------------------

def improve_answer(state: ReflectionState):

    prompt = f"""
    Improve the original answer using the critique.
    
    Question:
    {state["question"]}
    
    Original Answer:
    {state["answer"]}
    
    Critique:
    {state["critique"]}
    
    Return only the improved final answer. 
    """
    response = model.invoke(prompt)

    return {
        "final_answer": response.content
    }


# --------------------------------------------------
# 6. Build LangGraph
# --------------------------------------------------

builder = StateGraph(ReflectionState)

builder.add_node("generate", generate_answer)
builder.add_node("reflect", reflect_on_answer)
builder.add_node("improve", improve_answer)


# --------------------------------------------------
# 7. Define Graph Flow
# --------------------------------------------------

builder.add_edge(START, "generate")

builder.add_edge(
    "generate",
    "reflect"
)

builder.add_edge(
    "reflect",
    "improve"
)

builder.add_edge(
    "improve",
    END
)


# --------------------------------------------------
# 8. Compile Graph
# --------------------------------------------------

graph = builder.compile()

# --------------------------------------------------
# 9. Run Graph
# --------------------------------------------------

result = graph.invoke(
    {
        "question": "Explain why the sky appears blue.",
        "answer": "",
        "critique": "",
        "final_answer": ""
    }
)


# --------------------------------------------------
# 10. Print Results
# --------------------------------------------------

print("\n--- ORIGINAL ANSWER ---")
print(result["answer"])

print("\n--- CRITIQUE ---")
print(result["critique"])

print("\n--- IMPROVED ANSWER ---")
print(result["final_answer"])

