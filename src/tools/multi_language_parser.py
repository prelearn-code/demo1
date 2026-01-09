"""
多语言代码提取器
从 LLM 输出中提取不同语言的代码块
"""
import re
from typing import Optional, Tuple


def extract_code_with_language(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    从文本中提取代码块和语言标识

    Args:
        text: LLM 输出的文本

    Returns:
        (代码, 语言标识) 或 (None, None)
    """
    # 尝试匹配带语言标识的代码块: ```language\ncode\n```
    patterns = [
        r'```(\w+)\n(.*?)\n```',  # ```python\ncode\n```
        r'```(\w+)\r\n(.*?)\r\n```',  # Windows 换行
        r'```\s*(\w+)\s*\n(.*?)```',  # 允许空格
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            language = match.group(1).lower()
            code = match.group(2).strip()
            return code, language

    # 尝试匹配没有语言标识的代码块: ```\ncode\n```
    patterns_no_lang = [
        r'```\n(.*?)\n```',
        r'```\r\n(.*?)\r\n```',
        r'```(.*?)```',
    ]

    for pattern in patterns_no_lang:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = match.group(1).strip()
            return code, None  # 语言未知，需要自动检测

    # 如果没有代码块标记，返回整个文本
    return text.strip(), None


def language_name_to_standard(lang_name: str) -> str:
    """
    将各种语言名称统一为标准名称

    Args:
        lang_name: 语言名称（如 'py', 'js', 'cpp' 等）

    Returns:
        标准化的语言名称
    """
    mapping = {
        # Python
        'python': 'python',
        'py': 'python',
        'python3': 'python',

        # JavaScript
        'javascript': 'javascript',
        'js': 'javascript',
        'node': 'javascript',
        'nodejs': 'javascript',

        # TypeScript
        'typescript': 'typescript',
        'ts': 'typescript',

        # Java
        'java': 'java',

        # C++
        'c++': 'cpp',
        'cpp': 'cpp',
        'cxx': 'cpp',

        # C
        'c': 'c',

        # Go
        'go': 'go',
        'golang': 'go',

        # Rust
        'rust': 'rust',
        'rs': 'rust',
    }

    return mapping.get(lang_name.lower(), lang_name.lower())


# 使用示例
if __name__ == "__main__":
    # 测试用例
    test_cases = [
        # Python
        """
这是一个 Python 示例：
```python
def hello():
    print("Hello, World!")
hello()
```
        """,

        # JavaScript
        """
这是一个 JavaScript 示例：
```javascript
function hello() {
    console.log("Hello, World!");
}
hello();
```
        """,

        # C++
        """
这是一个 C++ 示例：
```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}
```
        """,

        # 没有语言标识
        """
```
print("Hello, World!")
```
        """,
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n测试 {i}:")
        print(f"输入:\n{test.strip()}")

        code, lang = extract_code_with_language(test)
        print(f"\n提取的代码:\n{code}")
        print(f"语言标识: {lang}")

        if lang:
            standard_lang = language_name_to_standard(lang)
            print(f"标准化语言: {standard_lang}")

        print("-" * 60)
