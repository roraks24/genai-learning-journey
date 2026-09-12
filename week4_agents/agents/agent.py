import json
import os

from dotenv import load_dotenv
from groq import Groq

from tools import calculator, get_weather, get_country_info


# ==================================================
# 1. Load environment variables
# ==================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(
    api_key=GROQ_API_KEY
)


# ==================================================
# 2. System prompt
# ==================================================

SYSTEM_PROMPT = """
You are a helpful assistant.

You have access to three tools:

1. calculator
   - Use it when mathematical calculation is required.

2. get_weather
   - Use it when the user asks for weather information.

3. get_country_info
   - Use it when the user asks for information about a country.

Use tools when appropriate.
If no tool is needed, answer directly.
After receiving a tool result, continue solving the user's request.
"""


# ==================================================
# 3. Tool schemas
# ==================================================

tools = [

    # ----------------------------------------------
    # Calculator
    # ----------------------------------------------

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
                        "description": (
                            "A mathematical expression "
                            "such as 25 * 17"
                        )
                    }
                },
                "required": ["expression"]
            }
        }
    },

    # ----------------------------------------------
    # Weather
    # ----------------------------------------------

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
    },

    # ----------------------------------------------
    # Country information
    # ----------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "get_country_info",
            "description": "Get basic information about a country.",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {
                        "type": "string",
                        "description": (
                            "The common name of the country."
                        )
                    }
                },
                "required": ["country"]
            }
        }
    }
]


# ==================================================
# 4. Tool registry
# ==================================================

TOOLS_MAP = {
    "calculator": calculator,
    "get_weather": get_weather,
    "get_country_info": get_country_info
}


# ==================================================
# 5. Ask the LLM
# ==================================================

def ask_llm(messages, tool_choice = "auto"):

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice
    )

    return response.choices[0].message


# ==================================================
# 6. Execute a tool
# ==================================================

def execute_tool(tool_call):

    tool_name = tool_call.function.name

    try:
        arguments = json.loads(
            tool_call.function.arguments
        )

    except json.JSONDecodeError:
        return "Tool arguments were not valid JSON."

    tool = TOOLS_MAP.get(tool_name)

    if tool is None:
        return f"Unknown tool: {tool_name}"

    try:
        return tool(**arguments)

    except Exception as e:
        return f"Tool execution error: {e}"


# ==================================================
# 7. Run agent
# ==================================================

def run_agent(
    user_input: str,
    max_steps: int = 10,
    tool_choice="auto"
) -> str:

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

        # Force tool only on first call.
        # After that, allow automatic decisions.
        current_tool_choice = (
            tool_choice if step == 0 else "auto"
        )

        try:
            message = ask_llm(
                messages,
                tool_choice=current_tool_choice
            )

        except Exception as e:
            return f"LLM request failed: {e}"

        if message.tool_calls:

            messages.append(message)

            for tool_call in message.tool_calls:

                print(
                    f"\nTool selected: "
                    f"{tool_call.function.name}"
                )

                print(
                    f"Arguments: "
                    f"{tool_call.function.arguments}"
                )

                result = execute_tool(tool_call)

                print(
                    f"Tool result: {result}"
                )

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

            continue

        return message.content

    return (
        "Agent stopped because the maximum "
        "number of steps was reached."
    )

# ==================================================
# 8. Tests
# ==================================================

if __name__ == "__main__":

    print("\n--- Test 1 ---")
    answer = run_agent(
        "What is 25 * 17?"
    )
    print("Final answer:", answer)

    print("\n--- Test 2 ---")
    answer = run_agent(
        "What is the weather in Jaipur?"
    )
    print("Final answer:", answer)

    print("\n--- Test 3 ---")
    answer = run_agent(
        "What is the capital of France?"
    )
    print("Final answer:", answer)

    print("\n--- Test 4 ---")
    answer = run_agent(
        "First calculate 25 * 17, "
        "then calculate the result plus 75."
    )
    print("Final answer:", answer)

    print("\n--- Test 5 ---")
    answer = run_agent(
        "Calculate 50 * 12 "
        "and tell me the weather in Jaipur."
    )
    print("Final answer:", answer)

    print("\n--- Test 6 ---")

    answer = run_agent(
    "Get information about India.",
    tool_choice={
        "type": "function",
        "function": {
            "name": "get_country_info"
        }
    }
)

    print("Final answer:", answer)

    print("\n--- Test 7: Invalid country argument ---")

answer = run_agent(
    "Use the get_country_info tool with an empty country name."
)

print("\nFinal answer:", answer)

print("\n--- Test 8: Tool result grounding ---")

answer = run_agent(
    "Use the get_country_info tool to get information about India. "
    "Only report information returned by the tool."
)

print("\nFinal answer:", answer)