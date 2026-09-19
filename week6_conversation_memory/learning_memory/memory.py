import json
import os

from dotenv import load_dotenv
from groq import Groq

from langchain_core.messages import (
    AIMessage,
    ToolMessage,
    HumanMessage,
    SystemMessage,
)

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.postgres import PostgresSaver

from tools import calculator

# -------------------------
# Environment
# -------------------------

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Groq API key not found in .env file")


client = Groq(api_key=GROQ_API_KEY)


# -------------------------
# System prompt
# -------------------------

SYSTEM_PROMPT = """
You are a helpful AI assistant with access to one tool.

AVAILABLE TOOL

1. calculator
   - Use for arithmetic and numerical calculations when accuracy matters.

TOOL-USAGE RULES

- Use the calculator when arithmetic is required.
- Do not use the calculator when it is unnecessary.
- Never invent tool results.
- Treat tool results as authoritative for the calculation.
- If a tool returns an error, explain the error clearly.
- Keep the final response concise.
"""


# -------------------------
# Tool schema
# -------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform mathematical calculations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression such as '25 * 17'."
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


TOOLS_MAP = {
    "calculator": calculator
}


# -------------------------
# Convert LangChain messages
# to Groq/OpenAI format
# -------------------------

def convert_messages(messages):

    converted = []

    for message in messages:

        if isinstance(message, SystemMessage):

            converted.append({
                "role": "system",
                "content": message.content
            })

        elif isinstance(message, HumanMessage):

            converted.append({
                "role": "user",
                "content": message.content
            })

        elif isinstance(message, AIMessage):

            converted_message = {
                "role": "assistant",
                "content": message.content or ""
            }

            if message.tool_calls:

                converted_message["tool_calls"] = [
                    {
                        "id": tool_call["id"],
                        "type": "function",
                        "function": {
                            "name": tool_call["name"],
                            "arguments": json.dumps(tool_call["args"])
                        }
                    }
                    for tool_call in message.tool_calls
                ]

            converted.append(converted_message)

        elif isinstance(message, ToolMessage):

            converted.append({
                "role": "tool",
                "tool_call_id": message.tool_call_id,
                "content": str(message.content)
            })

    return converted


# -------------------------
# LLM
# -------------------------

def ask_llm(messages):

    groq_messages = convert_messages(messages)

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        messages=groq_messages,
        tools=tools,
        tool_choice="auto"
    )

    return response.choices[0].message


# -------------------------
# LLM node
# -------------------------

def call_llm(state: MessagesState):

    messages = state["messages"]

    response = ask_llm(messages)

    tool_calls = []

    if response.tool_calls:

        for tool_call in response.tool_calls:

            tool_calls.append({
                "id": tool_call.id,
                "name": tool_call.function.name,
                "args": json.loads(tool_call.function.arguments),
                "type": "tool_call"
            })

    ai_message = AIMessage(
        content=response.content or "",
        tool_calls=tool_calls
    )

    return {
        "messages": [ai_message]
    }


# -------------------------
# Execute tool
# -------------------------

def execute_tool(tool_call):

    tool_name = tool_call["name"]
    arguments = tool_call["args"]

    tool = TOOLS_MAP.get(tool_name)

    if tool is None:
        return f"Error: tool not found: {tool_name}"

    try:
        return tool(**arguments)

    except Exception as e:
        return f"Tool execution error: {e}"


# -------------------------
# Tool node
# -------------------------

def run_tools(state: MessagesState):

    last_message = state["messages"][-1]

    tool_messages = []

    for tool_call in last_message.tool_calls:

        result = execute_tool(tool_call)

        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            )
        )

    return {
        "messages": tool_messages
    }


# -------------------------
# Routing
# -------------------------

def route_after_llm(state: MessagesState):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "run_tools"

    return END


# -------------------------
# Build graph
# -------------------------

builder = StateGraph(MessagesState)

builder.add_node("call_llm", call_llm)
builder.add_node("run_tools", run_tools)

builder.add_edge(START, "call_llm")

builder.add_conditional_edges(
    "call_llm",
    route_after_llm
)

builder.add_edge("run_tools", "call_llm")


# -------------------------
# Checkpointer
# -------------------------


with PostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:

    checkpointer.setup()

    graph = builder.compile(
        checkpointer=checkpointer
    )


# -------------------------
# Thread configuration
# -------------------------

    config = {
    "configurable": {
        "thread_id": "conversation_1"
    }
    }


# -------------------------
# Invocation 1
# -------------------------

    result_1 = graph.invoke(
    {
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": "what is my name?"
            }
        ]
    },
    config
    )

    print("Invocation 1:")
    print(result_1["messages"][-1].content)


