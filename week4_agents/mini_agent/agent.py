import json, os, requests
from dotenv import load_dotenv
from groq import Groq

from tools import calculator, get_country_info, get_weather, get_datetime, web_search,currency_converter

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Groq API key not found in .env file")

client = Groq(
    api_key=GROQ_API_KEY
)

SYSTEM_PROMPT = """
You are a helpful AI assistant with access to six tools.

AVAILABLE TOOLS

1. calculator
   - Use for arithmetic and numerical calculations when accuracy matters.

2. get_weather
   - Use for current weather information for a city.

3. get_country_info
   - Use for country information such as capital, region, and population.
   - Only report information returned by the tool.

4. currency_converter
   - Use for currency conversion and exchange-rate calculations.

5. web_search
   - Use for unknown, obscure, company-specific, current, recent,
     or externally verifiable information.
   - Use this tool instead of relying on your own memory when web
     verification is appropriate.
   - The only argument accepted by this tool is "query".
   - Never provide cursor, id, page, offset, or other navigation
     parameters.

6. get_datetime
   - Use for the current date and time.
   - Use the requested city, country, or timezone when provided.
   - If no location is provided, use the configured default timezone.

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
                        "description": "City name, such as Jaipur or London."
                    }
                },
                "required": ["city"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_country_info",
            "description": "Get country information such as capital, region, and population.",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {
                        "type": "string",
                        "description": "Country name, such as India or Japan."
                    }
                },
                "required": ["country"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "currency_converter",
            "description": "Convert an amount from one currency to another using an exchange rate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Amount of money to convert."
                    },
                    "from_currency": {
                        "type": "string",
                        "description": "Three-letter source currency code, such as USD or INR."
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "Three-letter target currency code, such as USD or INR."
                    }
                },
                "required": [
                    "amount",
                    "from_currency",
                    "to_currency"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the public web for unknown, obscure, "
                           "current, recent, company-specific, or externally "
                           "verifiable information. This tool accepts exactly "
                           "one argument named 'query'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A single natural-language search query. "
                                       "Do not provide cursor, id, page, offset, "
                                       "or other parameters."
                    }
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "Get the current date and time for a city or timezone. Use the configured default timezone when no location is provided.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location_or_timezone": {
                        "type": "string",
                        "description": "City, country, or IANA timezone such as Tokyo, India, Asia/Tokyo, or Asia/Kolkata."
                    }
                },
                "required": ["location_or_timezone"]
            }
        }
    }
]

TOOLS_MAP = {
    "calculator": calculator,
    "get_weather": get_weather,
    "get_country_info": get_country_info,
    "get_datetime": get_datetime,
    "web_search": web_search,
    "currency_converter": currency_converter    
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

def run_agent(
        user_input: str,
        max_steps: int=10,
        tool_choice= "auto"
) -> str:

    messages = [
        {
            "role" : "system",
            "content" : SYSTEM_PROMPT
        },
        {
            "role" : "user",
            "content" : user_input
        }
    ]

    for step in range(max_steps):

        current_tool_choice = (
            tool_choice if step == 0 else "auto"
        )

        try:
            message = ask_llm(
                messages,
                tool_choice=current_tool_choice
            )

        except Exception as e:
            return f"LLM  request failed: {e}"

        if message.tool_calls:
            messages.append(message)

            for tool_call in message.tool_calls:

                result = execute_tool(tool_call)

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

while True:
    print("==================================================")
    choice = input("Ask anything (press # to exit): ")

    if choice == "#":
        print("Exiting...")
        break

    answer = run_agent(choice)
    print()
    print("Result:")
    print(answer)
    print()