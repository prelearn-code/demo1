"""
LLM 基础设施层
封装 ChatOllama 客户端
"""
from .client import get_llm

__all__ = ["get_llm"]
