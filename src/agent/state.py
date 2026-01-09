"""
Agent 状态定义
使用 TypedDict 定义图的状态结构
"""
from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    Agent 的状态定义

    Attributes:
        messages: 对话历史记录
        code: 当前生成的代码
        execution_result: 代码执行结果
        error: 执行错误信息（原始字符串）
        iterations: 当前迭代次数
        structured_error: 结构化错误对象（新增）
        route_result: 错误路由结果（新增）
        test_input: 测试输入，用于 dry run（新增）
        reflection_history: 反思历史记录（新增）
        matched_rule_id: 匹配的规则ID（新增）
    """
    messages: List[BaseMessage]
    code: Optional[str]
    execution_result: Optional[str]
    error: Optional[str]
    iterations: int
    # 阶段三新增字段
    structured_error: Optional[Any]  # StructuredError 对象
    route_result: Optional[Dict[str, Any]]  # 路由结果
    test_input: Optional[Dict[str, Any]]  # 测试输入
    reflection_history: Optional[List[Any]]  # ReflectionEntry 列表
    matched_rule_id: Optional[str]  # 匹配的规则ID
