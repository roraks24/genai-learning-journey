from dataclasses import dataclass
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore

from langchain_huggingface import HuggingFaceEmbeddings


# --------------------------------------------------
# State
# --------------------------------------------------

class GraphState(TypedDict):
    query: str
    retrieved_memory: list[str]


# --------------------------------------------------
# Runtime Context
# --------------------------------------------------

@dataclass
class Context:
    user_id: str


# --------------------------------------------------
# Embedding Model
# --------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={
        "device": "cpu"
    },
    encode_kwargs={
        "normalize_embeddings": True
    }
)


# --------------------------------------------------
# Memory Store
# --------------------------------------------------

store = InMemoryStore(
    index={
        "dims": 384,
        "embed": embeddings,
        "fields": ["memory"]
    }
)


# --------------------------------------------------
# Memory Node
# --------------------------------------------------

def memory_node(
    state: GraphState,
    runtime: Runtime[Context]
):

    user_id = runtime.context.user_id

    namespace = (user_id, "preferences")

    results = runtime.store.search(
        namespace,
        query=state["query"],
        limit=3
    )

    retrieved_memories = []

    for result in results:
        retrieved_memories.append(
            result.value["memory"]
        )

    print(f"\nUser: {user_id}")
    print(f"Query: {state['query']}")
    print("\nRetrieved memories:")

    for memory in retrieved_memories:
        print(f"- {memory}")

    return {
        "retrieved_memory": retrieved_memories
    }


# --------------------------------------------------
# Graph
# --------------------------------------------------

builder = StateGraph(
    state_schema=GraphState,
    context_schema=Context
)

builder.add_node(
    "memory_node",
    memory_node
)

builder.add_edge(
    START,
    "memory_node"
)

builder.add_edge(
    "memory_node",
    END
)

graph = builder.compile(
    store=store
)


# --------------------------------------------------
# Add memories for User 1
# --------------------------------------------------

store.put(
    ("user_1", "preferences"),
    "memory_1",
    {
        "memory": "Rohit prefers Python for programming."
    }
)

store.put(
    ("user_1", "preferences"),
    "memory_2",
    {
        "memory": "Rohit is learning Generative AI and wants to become an AI Engineer."
    }
)

store.put(
    ("user_1", "preferences"),
    "memory_3",
    {
        "memory": "Rohit mainly works with VS Code for development."
    }
)

store.put(
    ("user_1", "preferences"),
    "memory_4",
    {
        "memory": "Rohit is building Rorak, an AI knowledge assistant."
    }
)


# --------------------------------------------------
# Add different memories for User 2
# --------------------------------------------------

store.put(
    ("user_2", "preferences"),
    "memory_1",
    {
        "memory": "User 2 prefers C++ for programming."
    }
)

store.put(
    ("user_2", "preferences"),
    "memory_2",
    {
        "memory": "User 2 is interested in web development."
    }
)


# --------------------------------------------------
# User 1 Query
# --------------------------------------------------

result_1 = graph.invoke(
    {
        "query": "Which programming language does this user prefer?",
        "retrieved_memory": []
    },
    context=Context(
        user_id="user_1"
    )
)

print("\nFinal state for user_1:")
print(result_1)


# --------------------------------------------------
# User 2 Query
# --------------------------------------------------

result_2 = graph.invoke(
    {
        "query": "What programming language does this user like?",
        "retrieved_memory": []
    },
    context=Context(
        user_id="user_2"
    )
)

print("\nFinal state for user_2:")
print(result_2)