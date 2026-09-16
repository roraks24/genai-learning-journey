from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class GraphState(TypedDict):
    a : int
    result : str
    formatted_result : str

def check_number(state: GraphState):
    a = state['a']

    if a % 2 == 0:
        return {"result" : "even"}

    else:
        return {"result" : "odd"}


def route_number(state: GraphState):
    return "even_number" if state["result"] == "even" else "odd_number"

def even_number(state: GraphState):
    return {"result": "a is even"}

def odd_number(state: GraphState):
    return {"result": "a is odd"}

    
def format_result(state: GraphState):
    formatted_result = state['result']

    return {"formatted_result" : formatted_result}

builder = StateGraph(GraphState)


builder.add_node("check_number", check_number)
builder.add_node("even_number", even_number)
builder.add_node("odd_number", odd_number)
builder.add_node("format_result", format_result)

builder.add_edge(START, "check_number")

builder.add_conditional_edges(
    "check_number", route_number
)

builder.add_edge("even_number", "format_result")
builder.add_edge("odd_number" ,"format_result")

builder.add_edge("format_result", END)

graph = builder.compile()

result = graph.invoke({
    "a" : 69
})

print(result)