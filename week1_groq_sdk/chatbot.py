import os
from dotenv import load_dotenv
from groq import Groq, APIConnectionError, RateLimitError, APIStatusError
import json

system_prompt = "You are a personal coding mentor. When the user describes a coding goal or problem, break it into a clear step-by-step plan or roadmap they can follow. When the user shares broken or buggy code, do not provide corrected code, even if asked directly. Instead, explain the underlying concept or bug clearly enough that the user can fix it themselves.When the user shares working code for review, point out specific weaknesses: poor structure, unclear naming, missing error handling, or inefficiencies — but do not rewrite the code yourself. Be direct and specific in feedback. Do not soften criticism unnecessarily, but stay constructive."

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def chat(temperature=1):
    
    if os.path.exists("conversation_history.json"):
        with open("conversation_history.json", "r") as f:
         conversation_history = json.load(f)

    else:
        conversation_history = []

    if not any(msg["role"] == "system" for msg in conversation_history):
        conversation_history.insert(0,{"role" : "system", "content" : system_prompt})

    while True:
        user_input = input("Enter (or press # to end): ")

        if user_input == "#":
         with open("conversation_history.json", "w") as f:
            json.dump(conversation_history, f)
            break

        conversation_history.append({"role": "user", "content": user_input})    
        
        try:
            chat_completion = client.chat.completions.create(
                messages=conversation_history,
                model="llama-3.3-70b-versatile",
                temperature=temperature,
            )

            
        except RateLimitError:
            print("Rate limit hit! You are sending requests too fast. Wait and try again later.")
            conversation_history.pop()
            continue

        except APIConnectionError:
            print("Network connection lost! Check your connection and try again.")
            conversation_history.pop()
            continue

        except APIStatusError as e:
            print(f"API returned an error. Status ({e.status_code}): {e.message}")
            conversation_history.pop()
            continue

        print(chat_completion.choices[0].message.content)
        conversation_history.append({"role": "assistant", "content": chat_completion.choices[0].message.content})
        print("#-----------------------------------------#")
        print(chat_completion.usage)
        print("#-----------------------------------------#")


while True:
    print("1. Enter the prompt"
          "\n2. Quit"
          )

    try:
        choice = int(input("Enter choice: "))
    except ValueError:
        print("invalid input!")
        continue

    if choice == 1:
        chat()
    elif choice == 2:
        break
    else:
        print("Enter a valid choice!")