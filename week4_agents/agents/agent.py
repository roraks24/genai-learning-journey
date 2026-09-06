import json
import os

from groq import Groq
from dotenv import load_dotenv

from tools import calculator, get_weather


# --------------------------------------------------
# 1. Load API key
# --------------------------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=GROQ_API_KEY)


SYSTEM_PROMPT = """
You are a helpful assistant.

You have access to two tools:

1. calculator
   - Use it when mathematical calculation is required.

2. get_weather
   - Use it when the user asks for weather information.

Use tools when appropriate.
If no tool is needed, answer directly.
After receiving a tool result, continue solving the user's request.
"""



tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a mathematical expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A mathematical expression such as 25 * 17"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city."
                    }
                },
                "required": ["city"]
            }
        }
    }
]


TOOLS_MAP = {
    "calculator": calculator,
    "get_weather": get_weather
}


def ask_llm(messages):

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    return response.choices[0].message


def execute_tool(tool_call):

    tool_name = tool_call.function.name

    try:
        arguments = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        return "Tool arguments were not valid JSON."

    tool = TOOLS_MAP.get(tool_name)

    if tool is None:
        return f"Unknown tool: {tool_name}"

    try:
        return tool(**arguments)
    except Exception as e:
        return f"Tool execution error: {e}"



def run_agent(user_input: str, max_steps: int = 10) -> str:

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    for step in range(max_steps):

        message = ask_llm(messages)


        if message.tool_calls:

            messages.append(message)

            for tool_call in message.tool_calls:

                print(f"\nTool selected: {tool_call.function.name}")
                print(f"Arguments: {tool_call.function.arguments}")

                result = execute_tool(tool_call)

                print(f"Tool result: {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

            continue

        return message.content

    return "Agent stopped because the maximum number of steps was reached."



if __name__ == "__main__":

    print("\n--- Test 1 ---")
    print(
        run_agent(
            "What is 25 * 17?"
        )
    )

    print("\n--- Test 2 ---")
    print(
        run_agent(
            "What is the weather in Jaipur?"
        )
    )

    print("\n--- Test 3 ---")
    print(
        run_agent(
            "What is the capital of France?"
        )
    )

    print("\n--- Test 4 ---")
    print(
        run_agent(
            "First calculate 25 * 17, then calculate the result plus 75."
        )
    )

    print("\n--- Test 5 ---")
    print(
        run_agent(
            "Calculate 50 * 12 and tell me the weather in Jaipur."
        )
    )