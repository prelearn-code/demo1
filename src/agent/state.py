"""
Agent 状态定义
使用 TypedDict 定义图的状态结构
"""
from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    Agent 的状态定义

    Attributes:
        messages: 对话历史记录
        code: 当前生成的代码
        execution_result: 代码执行结果
        error: 执行错误信息
        iterations: 当前迭代次数
    """
    messages: List[BaseMessage]
    code: Optional[str]
    execution_result: Optional[str]
    error: Optional[str]
    iterations: int
