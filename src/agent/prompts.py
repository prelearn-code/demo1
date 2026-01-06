"""
Prompt 模板管理
针对 Qwen2.5-Coder-7B 优化的提示词
"""

# Coder 节点的系统提示词
CODER_SYSTEM_PROMPT = """你是一个专业的 Python 程序员。

**任务规则:**
1. 只输出可执行的 Python 代码
2. 代码必须用 ```python 包裹
3. 不要输出任何解释或注释
4. 确保代码完整且可直接运行

**输出格式示例:**
```python
# 你的代码
print("Hello World")
```
"""

# Reflector 节点的系统提示词
REFLECTOR_SYSTEM_PROMPT = """你是一个代码调试专家。

**任务规则:**
1. 分析执行错误信息
2. 给出简洁的修复建议
3. 不要输出代码,只输出分析和建议
4. 使用中文回答

**输出格式:**
错误原因: [简短说明]
修复建议: [具体步骤]
"""


def get_coder_prompt(task: str, error: str = None) -> str:
    """
    构建 Coder 节点的提示词

    Args:
        task: 用户的编程任务
        error: 上一次执行的错误信息(可选)

    Returns:
        完整的提示词
    """
    if error:
        return f"""**用户任务:** {task}

**上次执行错误:**
{error}

**请修复上述错误,重新生成代码。**
"""
    else:
        return f"""**用户任务:** {task}

**请生成完整的 Python 代码。**
"""


def get_reflector_prompt(error: str) -> str:
    """
    构建 Reflector 节点的提示词

    Args:
        error: 执行错误信息

    Returns:
        完整的提示词
    """
    return f"""**执行错误:**
```
{error}
```

**请分析错误原因并给出修复建议。**
"""
