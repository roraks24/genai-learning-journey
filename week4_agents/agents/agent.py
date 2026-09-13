import json, os, requests

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

 # ============================================================
# DAY 25 — MULTI-TOOL + MULTI-STEP AGENT TESTS
# ============================================================

 print("\n--- Day 26 Test 1: Invalid Arguments ---")

answer = run_agent(
    "Use the weather tool with an empty city name."
)

print("\nFinal answer:", answer)

print("\n--- Day 26 Test 2: Malformed JSON ---")

from types import SimpleNamespace

fake_tool_call = SimpleNamespace(
    function=SimpleNamespace(
        name="get_weather",
        arguments='{"city": "Jaipur"'
    )
)

result = execute_tool(fake_tool_call)

print("Tool result:", result)

print("\n--- Day 26 Test 3: Unknown Tool ---")

fake_tool_call = SimpleNamespace(
    function = SimpleNamespace(
        name = "get_stock_price",
        arguments='{"symbol": "NVDA"}'
    )
)

result = execute_tool(fake_tool_call)

print("Tool result: ", result)

print("\n--- Day 26 Test 4: Tool Execution Error ---")

def failing_tool(city: str):
    raise RuntimeError("Simulated tool failure")

TOOLS_MAP["failing_tool"] = failing_tool

fake_tool_call = SimpleNamespace(
    function=SimpleNamespace(
        name="failing_tool",
        arguments='{"city": "Jaipur"}'
    )
)

result = execute_tool(fake_tool_call)

print("Tool result:", result)

del TOOLS_MAP["failing_tool"]




print("\n--- Day 26 Test 5: API Failure ---")

original_get = requests.get

def failing_get(*args, **kwargs):
    raise requests.RequestException("Simulated API failure")

requests.get = failing_get

result = get_country_info("India")

print("Tool result:", result)

requests.get = original_get




print("\n--- Day 26 Test 6: Retry Handling ---")

attempts = {"count": 0}

original_get = requests.get


def flaky_get(*args, **kwargs):
    attempts["count"] += 1

    if attempts["count"] < 3:
        raise requests.RequestException(
            f"Temporary failure on attempt {attempts['count']}"
        )

    return original_get(*args, **kwargs)


requests.get = flaky_get

for attempt in range(3):
    try:
        response = requests.get(
            "https://example.com",
            timeout=5
        )

        print(f"Request succeeded on attempt {attempt + 1}")
        break

    except requests.RequestException as e:
        print(f"Attempt {attempt + 1} failed: {e}")

requests.get = original_get





print("\n--- Day 26 Test 7: Loop Prevention ---")

answer = run_agent(
    "Keep calling the calculator tool with 1 + 1 repeatedly.",
    max_steps=3
)

print("\nFinal answer:", answer)




print("\n--- Day 26 Test 8: Timeout Handling ---")

original_get = requests.get


def timeout_get(*args, **kwargs):
    raise requests.Timeout("Simulated request timeout")


requests.get = timeout_get

result = get_country_info("India")

print("Tool result:", result)

requests.get = original_get


