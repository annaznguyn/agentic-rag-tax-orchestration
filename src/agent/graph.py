from langgraph.graph import StateGraph, START, END

from src.agent.state import State

from src.agent.node.initialise.extract import extract_query
from src.agent.node.initialise.suggest_deductions import suggest_deductions, add_suggestions
from src.agent.node.initialise.confirm_user import confirm_user, route_after_confirm
from src.agent.node.main_logic.retrieve import retrieve
from src.agent.node.main_logic.verify import verify


def build_graph():
    graph = StateGraph(State)

    graph.add_node("extract_query", extract_query)
    graph.add_node("suggest_deductions", suggest_deductions)
    graph.add_node("confirm_user", confirm_user)
    graph.add_node("add_suggestions", add_suggestions)
    graph.add_node("retrieve", retrieve)
    graph.add_node("verify", verify)

    graph.add_edge(START, "extract_query")
    graph.add_edge("extract_query", "suggest_deductions")
    graph.add_edge("suggest_deductions", "confirm_user")
    graph.add_conditional_edges(
        "confirm_user",
        route_after_confirm,
        {"add_suggestions": "add_suggestions", "retrieve": "retrieve"},
    )
    graph.add_edge("add_suggestions", "retrieve")
    graph.add_edge("retrieve", "verify")
    graph.add_edge("verify", END)

    return graph.compile()
