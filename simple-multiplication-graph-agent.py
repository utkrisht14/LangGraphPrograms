from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from langgraph.graph import START, END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode


load_dotenv()


# --------------------------------------------------
# 1. Create a tool
# --------------------------------------------------

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


tools = [multiply]


# --------------------------------------------------
# 2. Create the model and give it access to tools
# --------------------------------------------------

model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

model_with_tools = model.bind_tools(tools)


# --------------------------------------------------
# 3. Create the agent node
# --------------------------------------------------

def call_model(state: MessagesState):
    """
    Send all current messages to the model.

    The model may:
    1. Return a normal answer
    2. Request a tool call
    """

    response = model_with_tools.invoke(state["messages"])

    return {
        "messages": [response]
    }


# --------------------------------------------------
# 4. Decide what should run next
# --------------------------------------------------

def should_continue(state: MessagesState):
    """
    Check whether the latest AI message contains tool calls.
    """

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


# --------------------------------------------------
# 5. Build the graph
# --------------------------------------------------

builder = StateGraph(MessagesState)

builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")

builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END,
    },
)

builder.add_edge("tools", "agent")


# --------------------------------------------------
# 6. Compile the graph
# --------------------------------------------------

agent = builder.compile()


# --------------------------------------------------
# 7. Run the agent
# --------------------------------------------------

result = agent.invoke(
    {
        "messages": [
            HumanMessage(
                content="What is 27 multiplied by 14?"
            )
        ]
    }
)

print(result["messages"][-1].content)