from typing import List, Optional, TypedDict

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Shared state passed between agent nodes."""

    messages: List[BaseMessage]
    code: Optional[str]
    error: Optional[str]
    iterations: int
