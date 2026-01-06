from functools import lru_cache

from langchain_ollama import ChatOllama

from src.config import settings


def _build_llm() -> ChatOllama:
    return ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=0,
    )


@lru_cache(maxsize=1)
def get_llm() -> ChatOllama:
    """Return a cached ChatOllama client configured for deterministic coding tasks."""

    return _build_llm()
