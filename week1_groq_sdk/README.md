# Week 1 — Raw LLM API Chatbot

A command-line chatbot built using the **Groq Python SDK** and the **Llama 3.3 70B** model.

This project marks the beginning of my **60-day GenAI Learning Journey**, where I learn Generative AI by building projects from scratch instead of following tutorials. The focus of Week 1 was understanding how to interact directly with an LLM through its SDK before introducing frameworks such as LangChain.

---

## Learning Objectives

During Week 1, I focused on learning:

- Making direct LLM API calls using the Groq SDK
- Designing effective system prompts
- Building multi-turn conversations
- Managing conversation history
- Handling API errors gracefully
- Persisting chat history using JSON

---

## Features

- Multi-turn conversations using a persistent `conversation_history` list.
- Conversation history automatically loaded from and saved to a JSON file.
- Robust API error handling using:
  - `RateLimitError`
  - `APIConnectionError`
  - `APIStatusError`
- Custom coding mentor persona created using a system prompt.
- Interactive command-line interface.

---

## Project Structure

```text
week1_raw_api/
│
├── chatbot.py
├── conversation_history.json
├── persona.txt
├── requirements.txt
├── .env.example
└── README.md
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/roraks24/genai-learning-journey.git
cd genai-learning-journey/week1_raw_api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

**Windows (PowerShell)**

```powershell
.venv\Scripts\Activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file using `.env.example`.

```env
GROQ_API_KEY=your_groq_api_key
```

### 6. Run the chatbot

```bash
python chatbot.py
```

---

## Usage

- Select **1** to start a chat.
- Type your prompt and press Enter.
- Type **#** to end the current conversation.
- Select **2** to exit the application.

---

## Known Limitations

### 1. Manual history persistence

Conversation history is saved only when the user exits the chat normally. If the application is forcefully closed, the latest messages are lost.

### 2. Persona is advisory, not restrictive

The coding mentor persona influences how the assistant responds but does not prevent it from answering non-coding questions. Enforcing strict topic boundaries would require a stronger system prompt or explicit refusal logic.

---

## Tech Stack

- Python
- Groq Python SDK
- Llama 3.3 70B
- python-dotenv
- JSON

---

## Key Takeaways

By the end of Week 1, I understood:

- How LLM APIs work without abstraction frameworks.
- How multi-turn conversations are implemented.
- Prompt engineering fundamentals.
- Error handling for production-like CLI applications.
- Persistent conversation storage using JSON.

---

## Next Step

Week 2 focuses on rebuilding this chatbot using **LangChain**, introducing:

- Prompt Templates
- LCEL (LangChain Expression Language)
- Message History
- Output Parsers
- Structured Output with Pydantic