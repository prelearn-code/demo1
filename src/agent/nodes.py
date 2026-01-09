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
from .errors import ErrorParser, ReflectionEntry
from ..llm import get_llm
from ..tools import execute_code, extract_code
from ..strategies import ErrorRouter
from ..learning import RuleBase

# 全局规则库实例（在实际使用中可以从文件加载）
_rule_base = RuleBase()
_error_router = ErrorRouter(_rule_base)


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

    # 使用 Docker 沙箱执行代码（安全隔离）
    success, output = execute_code(code)

    if success:
        print(f"[Executor] ✓ 执行成功")
        print(f"输出:\n{output}")
        state["execution_result"] = output
        state["error"] = None
        state["structured_error"] = None
    else:
        print(f"[Executor] ✗ 执行失败")
        print(f"错误:\n{output}")
        state["error"] = output
        state["execution_result"] = None

        # 【阶段三新增】解析错误为结构化对象
        structured_error = ErrorParser.parse(output, code)
        state["structured_error"] = structured_error

        print(f"[Executor] 错误类型: {structured_error.error_type.value}")
        if structured_error.line_number:
            print(f"[Executor] 错误行号: {structured_error.line_number}")

    return state


def reflector_node(state: AgentState) -> AgentState:
    """
    Reflector 节点: 分析错误并给出建议（使用ErrorRouter）

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    print("\n[Reflector] 正在分析错误...")

    error = state.get("error", "")
    if not error:
        return state

    # 【阶段三新增】使用 ErrorRouter 进行智能路由
    structured_error = state.get("structured_error")
    if structured_error:
        print(f"\n[Reflector] 使用错误路由器处理 {structured_error.error_type.value} 错误")
        route_result = _error_router.route(state)
        state["route_result"] = route_result

        # 记录匹配的规则ID（用于统计）
        if "matched_rule" in route_result:
            state["matched_rule_id"] = route_result["matched_rule"]

        # 如果有执行追踪，添加到提示中
        suggestion = route_result.get("suggestion", "")
        trace = route_result.get("trace", "")

        # 构建增强的提示词
        enhanced_prompt = get_reflector_prompt(error)
        if suggestion:
            enhanced_prompt += f"\n\n【规则库建议】\n{suggestion}"
        if trace and trace != "无法执行追踪：缺少测试输入":
            enhanced_prompt += f"\n\n【执行追踪】\n{trace}"

        prompt = enhanced_prompt
    else:
        # 没有结构化错误，使用原始提示
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

    # 记录反思历史（用于学习）
    if structured_error:
        reflection = ReflectionEntry(
            iteration=state["iterations"],
            error=structured_error,
            diagnosis=response.content[:200],  # 简化存储
            correction_strategy=response.content[:200],
            corrected_code="",  # 将在下次迭代中更新
            success=False  # 将在验证后更新
        )

        if not state.get("reflection_history"):
            state["reflection_history"] = []
        state["reflection_history"].append(reflection)

    return state
