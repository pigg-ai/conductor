import os
import sys
from typing import Annotated, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

from src.core.logger import logger
from src.core.env import settings


@tool
def write_file(filename: str, content: str):
    """Write content to a file with the given filename.All the files will be written to 'output' directory. you should provide path of the file excluding 'output' directory."""
    fpath = os.path.join(sys.path[0], "output", filename)
    with open(fpath, "w") as f:
        f.write(content)
    msg = f"Successfully wrote to {filename}"
    logger.info(msg)
    return msg


tools = [write_file]
tool_node = ToolNode(tools)

# Initialize the language model and bind the tools
model = ChatOpenAI(
    model="gpt-4o-mini", temperature=0, api_key=settings.OPENAI_API_KEY
).bind_tools(tools)


# Function to decide whether to continue or end the conversation
def should_continue(state: MessagesState) -> Literal["tools", END]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END


# Function to call the model
def call_model(state: MessagesState):
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}


# Define the state graph
workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

# Initialize memory for state persistence
checkpointer = MemorySaver()

# Compile the graph into an application
app = workflow.compile(checkpointer=checkpointer)

# Define the initial system message to guide the agent
initial_messages = [
    SystemMessage(
        content=(
            "You are an software engineer. When given a coding task, "
            "you should generate the code and save it to a file using the 'write_file' tool. "
        )
    )
]


def run():
    # Invoke the application with user input
    final_state = app.invoke(
        {
            "messages": initial_messages
            + [
                HumanMessage(
                    content="Write a Python function that calculates the factorial of a number and save it to 'factorial.py'"
                )
            ]
        },
        config={"configurable": {"thread_id": 42}},
    )

    # Output the agent's final response
    print(final_state["messages"][-1].content)
