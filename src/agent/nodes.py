from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from src.agent.prompts import (
    CODER_SYSTEM_PROMPT,
    CODER_USER_PROMPT,
    REFLECTOR_SYSTEM_PROMPT,
    REFLECTOR_USER_PROMPT,
)
from src.agent.state import AgentState
from src.config import settings
from src.llm.client import get_llm
from src.tools.parser import clean_code_block
from src.tools.sandbox import run_code


def coder_node(state: AgentState) -> AgentState:
    llm = get_llm()

    instruction = state["messages"][0].content if state["messages"] else ""
    user_prompt = CODER_USER_PROMPT.format(
        instruction=instruction,
        error=state.get("error") or "无",
        previous_code=state.get("code") or "",
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=CODER_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )

    response = llm.invoke(prompt.format_messages())
    code = clean_code_block(response.content)

    updated_messages = [*state["messages"], AIMessage(content=response.content)]
    return {
        "messages": updated_messages,
        "code": code,
        "error": None,
        "iterations": state["iterations"] + 1,
    }


def executor_node(state: AgentState) -> AgentState:
    code = state.get("code") or ""
    if not code:
        return {
            "messages": [*state["messages"], AIMessage(content="No code to execute.")],
            "code": code,
            "error": "缺少可执行的代码",
            "iterations": state["iterations"],
        }

    result = run_code(code)

    message_content_parts = []
    if result.stdout:
        message_content_parts.append(f"stdout:\n{result.stdout}")
    if result.stderr:
        message_content_parts.append(f"stderr:\n{result.stderr}")
    message_content = "\n\n".join(message_content_parts) or "Execution completed with no output."

    error_text = result.stderr if result.returncode != 0 else None

    return {
        "messages": [*state["messages"], AIMessage(content=message_content)],
        "code": code,
        "error": error_text,
        "iterations": state["iterations"],
    }


def reflector_node(state: AgentState) -> AgentState:
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=REFLECTOR_SYSTEM_PROMPT),
            HumanMessage(
                content=REFLECTOR_USER_PROMPT.format(
                    error=state.get("error") or "未知错误",
                    code=state.get("code") or "",
                )
            ),
        ]
    )

    response = llm.invoke(prompt.format_messages())
    feedback = response.content

    guidance_message = HumanMessage(content=f"需要修复：\n{feedback}")

    return {
        "messages": [*state["messages"], guidance_message],
        "code": state.get("code"),
        "error": None,
        "iterations": min(state["iterations"], settings.MAX_ITERATIONS),
    }
