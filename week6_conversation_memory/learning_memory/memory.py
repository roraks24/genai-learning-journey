from typing import TypedDict
from langgraph.graph import StateGraph, MessagesState,START, END
from langgraph.checkpoint.memory import InMemorySaver
import json, os
from dotenv import load_dotenv
from groq import Groq
from tools import calculator, get_country_info, get_weather, get_datetime, web_search,currency_converter


class GraphState(MessagesState):
    pass



load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Groq API key not found in .env file")

client = Groq(
    api_key=GROQ_API_KEY
)

SYSTEM_PROMPT = """
You are a helpful AI assistant with access to tools.

AVAILABLE TOOLS

1. calculator
   - Use for arithmetic and numerical calculations when accuracy matters.

TOOL-USAGE RULES

- Use a tool when it is more appropriate than answering directly.
- Do not use a tool when it is unnecessary.
- For unknown or externally verifiable information, prefer web_search.
- When a task requires multiple steps, use the result of one tool
  call as input to the next tool call when appropriate.
- Never invent tool results.
- Treat tool results as authoritative for the operation performed.
- If a tool returns an error, explain the error clearly.
- Do not fabricate a successful result after a tool failure.
- Keep the final response concise and directly answer the user's request.
"""

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
                        "description": "Mathematical expression to calculate, such as '25 * 17'."
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

def ask_llm(messages, tool_choice="auto"):


    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        messages=messages,
        tool_choice=tool_choice,
        tools=tools
    )

    return response.choices[0].message

def call_llm(state: GraphState):
    messages = state['messages']

    response = ask_llm(messages)

    return {"messages" : messages + [response]}


def execute_tool(tool_call):

    tool_name = tool_call.function.name

    try:
        arguments = json.loads(
            tool_call.function.arguments
        )

    except json.JSONDecodeError:
        return "Tool arguements were not valid JSON"

    tool = TOOLS_MAP.get(tool_name)

    if not tool:
        return f"Error: tool not found {tool_name}"

    try:
        return tool(**arguments)

    except Exception as e:
        return f"Tool execution error: {e}"

def run_tools(state: GraphState):

    messages = state["messages"]

    last_message = messages[-1]

    new_message = messages.copy()

    for tool_call in last_message.tool_calls:

        result = execute_tool(tool_call)

        new_message.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
        })

    return {"messages" : new_message}

def route_after_llm(state: GraphState):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "run_tools"

    return END

builder = StateGraph(MessagesState)

builder.add_node("call_llm", call_llm)
builder.add_node("run_tools", run_tools)

builder.add_edge(START, "call_llm")

builder.add_conditional_edges(
    "call_llm", route_after_llm
)

builder.add_edge("run_tools", "call_llm")

checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)

result = graph.invoke({
    "messages": [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": "125 * 8"
        }
    ]

},
    {
        "configurable" : {
            "thread_id" : "conversation_1"
        }
    }
)

print(result)