import re
from typing import Optional


_CODE_BLOCK_PATTERN = re.compile(r"```(?:python)?\n(.*?)```", re.DOTALL | re.IGNORECASE)


def clean_code_block(content: str) -> str:
    """Extract and sanitize the Python code block from model output."""

    match: Optional[re.Match[str]] = _CODE_BLOCK_PATTERN.search(content)
    if match:
        return match.group(1).strip()

    stripped = content.replace("Here is the code:", "").strip()
    return stripped
