from langgraph.graph import StateGraph, START, END

from src.agent.state import State

from src.agent.node.initialise.extract import extract_query
from src.agent.node.initialise.create_state import create_state
from src.agent.node.initialise.suggest_deductions import suggest_deductions, add_suggestions
from src.agent.node.initialise.confirm_user import confirm_user


def build_graph():
    graph = StateGraph(State)

    graph.add_node("extract_query", extract_query)
    graph.add_node("create_state", create_state)
    graph.add_node("suggest_deductions", suggest_deductions)
    graph.add_node("confirm_user", confirm_user)
    graph.add_node("add_suggestions", add_suggestions)

    graph.add_edge(START, "extract_query")
    graph.add_edge("extract_query", "create_state")
    graph.add_edge("create_state", "suggest_deductions")
    graph.add_edge("suggest_deductions", "confirm_user")    
    graph.add_edge("confirm_user", "add_suggestions")       # user accepts deductions
    graph.add_edge("confirm_user", END)                     # user rejects deductions
    graph.add_edge("add_suggestions", END)

    return graph.compile()