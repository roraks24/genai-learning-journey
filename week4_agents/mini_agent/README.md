# Multi-Tool AI Agent

A lightweight AI agent built with Python and Groq that can dynamically select and execute tools based on a user's request.

The project demonstrates core agent engineering concepts including tool calling, multi-tool execution, multi-step workflows, argument validation, error handling, API integration, and loop prevention.

---

## Features

- LLM-powered tool selection using Groq
- Multi-tool execution
- Multi-step tool workflows
- Tool argument parsing and validation
- Graceful handling of tool failures
- API timeout and error handling
- Maximum-step protection against infinite agent loops
- Interactive command-line interface
- Environment-based secret management

---

## Architecture

```text
                         User
                           |
                           v
                    +--------------+
                    |   Agent      |
                    |   (agent.py) |
                    +------+-------+
                           |
                           v
                    +--------------+
                    |   Groq LLM   |
                    +------+-------+
                           |
                    Tool selection
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
    Calculator         Weather         Country Info
          |                |                |
          +----------------+----------------+
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      Currency         Web Search        Date/Time
                           |
                           v
                     Tool Result
                           |
                           v
                    Message History
                           |
                           v
                       Groq LLM
                           |
                           v
                     Final Answer