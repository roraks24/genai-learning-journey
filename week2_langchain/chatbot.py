from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()

store = {}


template = ChatPromptTemplate(
    [
        ("system", "You are a coding assistant. Your name is {name}."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}")
    ]
)


def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def chat():

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_retries=2
    )

    parser = StrOutputParser()

    chain = template | llm | parser

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history"
    )

    while True:

        user_input = input("Enter prompt (press # to end chat): ")

        if user_input == "#":
            break

        response = chain_with_history.invoke(
            {
                "name": "rorak",
                "input": user_input
            },
            config={
                "configurable": {
                    "session_id": "session1"
                }
            }
        )

        print(">>", response)
        print()


while True:

    print("1. Start a chat")
    print("2. Quit")

    choice = input("Enter your choice: ")

    if choice == "1":
        chat()

    elif choice == "2":
        break

    else:
        print("Enter a valid choice!")