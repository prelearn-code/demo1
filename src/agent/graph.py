"""
LangGraph 工作流构建
定义 Agent 的状态机流转
"""
from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import coder_node, executor_node, reflector_node
from ..config import settings


def should_continue(state: AgentState) -> str:
    """
    决策函数: 判断是否继续迭代

    流程:
    1. 如果执行成功 -> END
    2. 如果有错误且未超过最大迭代次数 -> reflector
    3. 如果超过最大迭代次数 -> END

    Args:
        state: 当前状态

    Returns:
        下一个节点名称或 END
    """
    # 检查是否成功
    if state.get("execution_result") and not state.get("error"):
        return END

    # 检查迭代次数
    if state.get("iterations", 0) >= settings.max_iterations:
        print(f"\n⚠️  已达到最大迭代次数 ({settings.max_iterations}),停止执行")
        return END

    # 有错误且未超过次数,继续反思
    if state.get("error"):
        return "reflector"

    return END


def create_graph():
    """
    创建 LangGraph 工作流

    流程图:
    START -> coder -> executor -> [判断]
                                    ├─> END (成功)
                                    └─> reflector -> coder (失败,继续迭代)

    Returns:
        编译后的图
    """
    # 创建状态图
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("coder", coder_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("reflector", reflector_node)

    # 设置入口点
    workflow.set_entry_point("coder")

    # 添加边
    workflow.add_edge("coder", "executor")
    workflow.add_conditional_edges(
        "executor",
        should_continue,
        {
            "reflector": "reflector",
            END: END
        }
    )
    workflow.add_edge("reflector", "coder")

    # 编译图
    return workflow.compile()
