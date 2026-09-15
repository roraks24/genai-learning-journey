from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class GraphState(TypedDict):
    a : int
    b : int
    c : int
    addition : int
    multiplication : int
    formatted_result : str

def add_numbers(state: GraphState):
    a = state["a"]
    b = state["b"]
    addition = a + b

    return {"addition": addition}

def multiply_numbers(state: GraphState):
    c = state["c"]
    addition = state["addition"]
    multiplication = c*addition

    return {"multiplication" : multiplication}


def format_result(state: GraphState):
    multiplication = state["multiplication"]
    formatted_result = f"when c is multiplied by the sum of a and b it gives: {multiplication}"

    return {"formatted_result" : formatted_result}


builder = StateGraph(GraphState)

builder.add_node("add_numbers", add_numbers)
builder.add_node("multiply_numbers", multiply_numbers)
builder.add_node("format_result", format_result)

builder.add_edge(START, "add_numbers")
builder.add_edge("add_numbers", "multiply_numbers")
builder.add_edge("multiply_numbers", "format_result")
builder.add_edge("format_result", END)

graph = builder.compile()

result = graph.invoke({
    "a" : 20,
    "b" : 30,
    "c" : 2
})

print(result)



