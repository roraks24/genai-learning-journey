from dataclasses import dataclass
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore



class GraphState(TypedDict):
    language: str
    retrieved_memory: str



@dataclass
class Context:
    user_id: str



store = InMemoryStore()



def memory_node(
    state: GraphState,
    runtime: Runtime[Context]
):
    user_id = runtime.context.user_id

    
    namespace = (user_id, "preferences")

    
    runtime.store.put(
        namespace,
        "favorite_language",
        {
            "language": state["language"]
        }
    )

    
    result = runtime.store.get(
        namespace,
        "favorite_language"
    )

    print(f"\nUser: {user_id}")
    print(f"Stored memory: {result}")
    print(f"Retrieved value: {result.value}")

    return {
        "retrieved_memory": result.value["language"]
    }




builder = StateGraph(
    state_schema=GraphState,
    context_schema=Context
)

builder.add_node("memory_node", memory_node)

builder.add_edge(START, "memory_node")
builder.add_edge("memory_node", END)



graph = builder.compile(
    store=store
)



result_1 = graph.invoke(
    {
        "language": "python",
        "retrieved_memory": ""
    },
    context=Context(
        user_id="user_1"
    )
)

print("\nFinal state for user_1:")
print(result_1)



result_2 = graph.invoke(
    {
        "language": "c++",
        "retrieved_memory": ""
    },
    context=Context(
        user_id="user_2"
    )
)

print("\nFinal state for user_2:")
print(result_2)



user_1_memory = store.get(
    ("user_1", "preferences"),
    "favorite_language"
)

user_2_memory = store.get(
    ("user_2", "preferences"),
    "favorite_language"
)

print("\n--- Memory Isolation Test ---")

print("User 1:", user_1_memory.value)
print("User 2:", user_2_memory.value)