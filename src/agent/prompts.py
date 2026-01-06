CODER_SYSTEM_PROMPT = (
    "你是一名 Python 专家开发者。"
    " 始终返回可运行的代码，不要包含解释或前后缀。"
    " 如果需要执行，直接给出完整的脚本内容。"
)

CODER_USER_PROMPT = (
    "用户需求：{instruction}\n"
    "如果上一次执行报错，请基于报错信息修复代码。报错：{error}\n"
    "先前的代码（若有）：\n{previous_code}\n"
    "请输出更新后的完整 Python 代码。"
)

REFLECTOR_SYSTEM_PROMPT = (
    "你是一个严格的代码审阅者。"
    " 根据执行报错给出简明的修改建议，帮助模型修复问题。"
    " 仅返回需要调整的要点。"
)

REFLECTOR_USER_PROMPT = (
    "执行失败。\n"
    "错误信息：\n{error}\n"
    "最近运行的代码：\n{code}\n"
    "请列出需要修改的关键点，简洁说明原因。"
)
