"""
ChatOllama 客户端封装
提供单例模式的 LLM 实例
"""
from langchain_ollama import ChatOllama
from ..config import settings


_llm_instance = None


def get_llm() -> ChatOllama:
    """
    获取 LLM 实例 (单例模式)

    Returns:
        ChatOllama: 配置好的 Ollama 客户端
    """
    global _llm_instance

    if _llm_instance is None:
        _llm_instance = ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=settings.temperature,
        )
        print(f"✓ LLM 已初始化: {settings.ollama_model}")

    return _llm_instance
