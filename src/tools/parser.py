"""
输出解析器
用于从 LLM 输出中提取代码
"""
import re


def extract_code(text: str) -> str:
    """
    从文本中提取 Python 代码块

    支持格式:
    1. ```python ... ```
    2. ``` ... ```
    3. 纯代码(无标记)

    Args:
        text: LLM 的原始输出

    Returns:
        提取出的代码
    """
    # 尝试匹配 ```python ... ```
    pattern1 = r"```python\s*(.*?)\s*```"
    match = re.search(pattern1, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 尝试匹配 ``` ... ```
    pattern2 = r"```\s*(.*?)\s*```"
    match = re.search(pattern2, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 如果没有代码块标记,返回原文本
    # 但需要清理常见的前缀
    text = text.strip()
    prefixes = [
        "Here is the code:",
        "这是代码:",
        "以下是代码:",
        "代码如下:",
    ]
    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()

    return text
