from langgraph.graph import END, StateGraph

from src.agent.nodes import coder_node, executor_node, reflector_node
from src.agent.state import AgentState
from src.config import settings


def _route_after_execution(state: AgentState) -> str:
    if state.get("error") and state["iterations"] < settings.MAX_ITERATIONS:
        return "reflector"
    return "end"


def create_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("coder", coder_node)
    graph.add_node("executor", executor_node)
    graph.add_node("reflector", reflector_node)

    graph.set_entry_point("coder")
    graph.add_edge("coder", "executor")
    graph.add_conditional_edges(
        "executor",
        _route_after_execution,
        {
            "reflector": "reflector",
            "end": END,
        },
    )
    graph.add_edge("reflector", "coder")

    return graph.compile()
