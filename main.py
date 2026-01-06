import argparse
from typing import Any

from langchain_core.messages import HumanMessage

from src.agent.graph import create_agent_graph
from src.agent.state import AgentState
from src.config import settings


def build_initial_state(prompt: str) -> AgentState:
    return {
        "messages": [HumanMessage(content=prompt)],
        "code": None,
        "error": None,
        "iterations": 0,
    }


def run_agent(prompt: str) -> AgentState:
    graph = create_agent_graph()
    initial_state = build_initial_state(prompt)
    return graph.invoke(initial_state)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local coding agent")
    parser.add_argument("prompt", help="Coding instruction to pass to the agent")
    args = parser.parse_args()

    final_state = run_agent(args.prompt)

    print("=== Agent Summary ===")
    print(f"Model: {settings.OLLAMA_MODEL}")
    print(f"Iterations: {final_state['iterations']}")

    if final_state.get("error"):
        print("Execution failed:\n")
        print(final_state["error"])
    else:
        print("Execution succeeded. Latest code:\n")
        print(final_state.get("code") or "<no code generated>")

    last_message_content: str | None = None
    if final_state["messages"]:
        last_message_content = final_state["messages"][-1].content

    if last_message_content:
        print("\nLast message:\n")
        print(last_message_content)


if __name__ == "__main__":
    main()
