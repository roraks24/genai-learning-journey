# Week 2 — LangChain Fundamentals

In Week 2, I migrated my Week 1 raw Groq SDK chatbot to **LangChain** to understand why frameworks exist and how they simplify building LLM-powered applications.

Instead of manually managing prompts, conversation history, and outputs, I learned how LangChain provides reusable abstractions for these common tasks.

---

## Learning Objectives

During Week 2, I learned:

- Integrating Groq with LangChain
- Building prompts using `ChatPromptTemplate`
- Using LCEL (LangChain Expression Language)
- Managing conversation history with `RunnableWithMessageHistory`
- Parsing model outputs with `StrOutputParser`
- Generating structured outputs using Pydantic models
- Extracting structured information from natural language

---

## Project Structure

```text
week2_langchain/
│
├── chatbot.py
├── structured_output.py
├── models.py
├── README.md
├── requirements.txt
└── .env.example
```

---

## Files

### chatbot.py

A CLI chatbot demonstrating:

- ChatGroq
- ChatPromptTemplate
- LCEL (`template | llm | parser`)
- RunnableWithMessageHistory
- StrOutputParser
- Session-based conversation memory

---

### structured_output.py

Demonstrates how to extract structured information from user input using:

- `with_structured_output()`
- Pydantic models
- Automatic validation
- Resume information extraction

---

### models.py

Contains the Pydantic models used for structured output.

---

## Concepts Learned

### ChatPromptTemplate

Creates reusable prompts with placeholders instead of manually building message lists.

### LCEL (LangChain Expression Language)

Allows components to be connected using the pipe (`|`) operator.

Example:

```python
chain = template | llm | parser
```

---

### RunnableWithMessageHistory

Automatically manages conversation history instead of manually appending messages.

---

### StrOutputParser

Converts the model response into a plain Python string.

---

### Structured Output

Instead of asking the model to return JSON manually, LangChain validates the response against a Pydantic model and returns a Python object.

---

## Tech Stack

- Python
- LangChain
- LangChain Groq
- Groq API
- Pydantic
- python-dotenv

---

## Key Takeaways

By the end of Week 2, I understood:

- Why LangChain exists
- How prompt templates improve code reusability
- How LCEL builds readable LLM pipelines
- How LangChain manages conversation history
- The difference between text output and structured output
- How Pydantic enables reliable data extraction from LLMs

---

## Next Step

Week 3 focuses on Retrieval-Augmented Generation (RAG), where I will learn:

- Embeddings
- Vector Databases
- Chunking
- Retrieval
- Building a complete RAG pipeline