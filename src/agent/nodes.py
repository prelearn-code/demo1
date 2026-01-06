"""
Agent 节点逻辑
定义图中各个节点的具体实现
"""
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from .state import AgentState
from .prompts import (
    CODER_SYSTEM_PROMPT,
    REFLECTOR_SYSTEM_PROMPT,
    get_coder_prompt,
    get_reflector_prompt
)
from ..llm import get_llm
from ..tools import execute_code, extract_code


def coder_node(state: AgentState) -> AgentState:
    """
    Coder 节点: 生成代码

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    print("\n[Coder] 正在生成代码...")

    # 获取用户任务
    task = state["messages"][0].content if state["messages"] else ""

    # 构建提示词
    prompt = get_coder_prompt(task, state.get("error"))

    # 调用 LLM
    llm = get_llm()
    messages = [
        SystemMessage(content=CODER_SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages)

    # 提取代码
    code = extract_code(response.content)

    # 更新状态
    state["code"] = code
    state["messages"].append(AIMessage(content=code))
    state["iterations"] += 1

    print(f"[Coder] 代码已生成 (迭代 {state['iterations']})")
    print(f"```python\n{code}\n```")

    return state


def executor_node(state: AgentState) -> AgentState:
    """
    Executor 节点: 执行代码

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    print("\n[Executor] 正在执行代码...")

    code = state.get("code", "")
    if not code:
        state["error"] = "没有代码可执行"
        return state

    # 执行代码
    success, output = execute_code(code)

    if success:
        print(f"[Executor] ✓ 执行成功")
        print(f"输出:\n{output}")
        state["execution_result"] = output
        state["error"] = None
    else:
        print(f"[Executor] ✗ 执行失败")
        print(f"错误:\n{output}")
        state["error"] = output
        state["execution_result"] = None

    return state


def reflector_node(state: AgentState) -> AgentState:
    """
    Reflector 节点: 分析错误并给出建议

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    print("\n[Reflector] 正在分析错误...")

    error = state.get("error", "")
    if not error:
        return state

    # 构建提示词
    prompt = get_reflector_prompt(error)

    # 调用 LLM
    llm = get_llm()
    messages = [
        SystemMessage(content=REFLECTOR_SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages)

    print(f"[Reflector] 分析结果:\n{response.content}")
    state["messages"].append(AIMessage(content=response.content))

    return state
