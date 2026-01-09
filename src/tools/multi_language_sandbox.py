"""
多语言代码执行沙箱
支持 Python, JavaScript, Java, C++, Go, Rust 等语言
"""
import docker
import re
from typing import Tuple, Optional
from enum import Enum


class Language(Enum):
    """支持的编程语言"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    C = "c"
    TYPESCRIPT = "typescript"


# 语言配置
LANGUAGE_CONFIGS = {
    Language.PYTHON: {
        "image": "python:3.11-alpine",
        "command": lambda code: ["python", "-c", code],
        "file_ext": ".py",
        "compile": False
    },
    Language.JAVASCRIPT: {
        "image": "node:18-alpine",
        "command": lambda code: ["node", "-e", code],
        "file_ext": ".js",
        "compile": False
    },
    Language.TYPESCRIPT: {
        "image": "node:18-alpine",
        "command": lambda code: ["sh", "-c", f"echo '{code}' > /tmp/code.ts && npx -y ts-node /tmp/code.ts"],
        "file_ext": ".ts",
        "compile": False
    },
    Language.JAVA: {
        "image": "openjdk:17-alpine",
        "command": lambda code: [
            "sh", "-c",
            f"echo '{code}' > Main.java && javac Main.java && java Main"
        ],
        "file_ext": ".java",
        "compile": True
    },
    Language.CPP: {
        "image": "gcc:12-alpine",
        "command": lambda code: [
            "sh", "-c",
            f"echo '{code}' > /tmp/code.cpp && g++ -o /tmp/code /tmp/code.cpp && /tmp/code"
        ],
        "file_ext": ".cpp",
        "compile": True
    },
    Language.C: {
        "image": "gcc:12-alpine",
        "command": lambda code: [
            "sh", "-c",
            f"echo '{code}' > /tmp/code.c && gcc -o /tmp/code /tmp/code.c && /tmp/code"
        ],
        "file_ext": ".c",
        "compile": True
    },
    Language.GO: {
        "image": "golang:1.21-alpine",
        "command": lambda code: [
            "sh", "-c",
            f"echo '{code}' > /tmp/main.go && cd /tmp && go run main.go"
        ],
        "file_ext": ".go",
        "compile": False
    },
    Language.RUST: {
        "image": "rust:1.75-alpine",
        "command": lambda code: [
            "sh", "-c",
            f"echo '{code}' > /tmp/main.rs && rustc /tmp/main.rs -o /tmp/main && /tmp/main"
        ],
        "file_ext": ".rs",
        "compile": True
    }
}


def detect_language(code: str) -> Language:
    """
    自动检测代码语言

    Args:
        code: 源代码

    Returns:
        检测到的语言
    """
    # Python 特征
    if re.search(r'\bdef\s+\w+\s*\(|import\s+\w+|from\s+\w+\s+import|print\s*\(', code):
        return Language.PYTHON

    # JavaScript/TypeScript 特征
    if re.search(r'\bconst\s+\w+|let\s+\w+|var\s+\w+|function\s+\w+|console\.log|=>|require\(', code):
        if re.search(r':\s*(string|number|boolean)|interface\s+\w+|type\s+\w+\s*=', code):
            return Language.TYPESCRIPT
        return Language.JAVASCRIPT

    # Java 特征
    if re.search(r'\bpublic\s+class\s+\w+|public\s+static\s+void\s+main|System\.out\.print', code):
        return Language.JAVA

    # C++ 特征
    if re.search(r'#include\s*<iostream>|std::cout|std::cin|namespace\s+std', code):
        return Language.CPP

    # C 特征
    if re.search(r'#include\s*<stdio\.h>|printf\s*\(|scanf\s*\(', code):
        return Language.C

    # Go 特征
    if re.search(r'\bpackage\s+main|func\s+main\s*\(\s*\)|import\s+\(|fmt\.Print', code):
        return Language.GO

    # Rust 特征
    if re.search(r'\bfn\s+main\s*\(\s*\)|println!\s*\(|use\s+std::', code):
        return Language.RUST

    # 默认返回 Python
    return Language.PYTHON


def execute_code_multi_language(
    code: str,
    language: Optional[Language] = None,
    timeout: int = 10
) -> Tuple[bool, str, Language]:
    """
    执行多语言代码

    Args:
        code: 源代码
        language: 指定语言（None 则自动检测）
        timeout: 超时时间(秒)

    Returns:
        (是否成功, 输出或错误信息, 使用的语言)
    """
    # 自动检测语言
    if language is None:
        language = detect_language(code)

    print(f"[MultiLanguage] 检测到语言: {language.value}")

    # 获取语言配置
    if language not in LANGUAGE_CONFIGS:
        return False, f"不支持的语言: {language.value}", language

    config = LANGUAGE_CONFIGS[language]

    client = None
    container = None

    try:
        # 初始化 Docker 客户端
        client = docker.from_env()

        # 转义代码中的单引号（用于 shell 命令）
        safe_code = code.replace("'", "'\"'\"'")

        # 创建并启动容器
        container = client.containers.run(
            image=config["image"],
            command=config["command"](safe_code),
            detach=True,
            mem_limit="256m",  # 编译型语言需要更多内存
            cpu_quota=50000,
            network_disabled=True,
            remove=False,
        )

        # 等待容器执行完成
        result = container.wait(timeout=timeout)

        # 获取输出
        logs = container.logs(stdout=True, stderr=True).decode('utf-8')

        # 检查退出码
        exit_code = result.get('StatusCode', -1)

        # 删除容器
        try:
            container.remove(force=True)
        except:
            pass

        if exit_code == 0:
            return True, logs, language
        else:
            return False, logs, language

    except docker.errors.ImageNotFound:
        return False, (
            f"Docker 镜像未找到: {config['image']}\n"
            f"请先拉取镜像: docker pull {config['image']}"
        ), language

    except docker.errors.APIError as e:
        return False, f"Docker API 错误: {str(e)}\n请确保 Docker 服务已启动", language

    except Exception as e:
        # 清理容器
        if container:
            try:
                container.remove(force=True)
            except:
                pass

        # 检查超时
        if "timeout" in str(e).lower() or "timed out" in str(e).lower():
            return False, f"执行超时 (>{timeout}秒)", language

        return False, f"执行错误: {str(e)}", language


def get_supported_languages() -> list:
    """获取支持的语言列表"""
    return [lang.value for lang in Language]


# 使用示例
if __name__ == "__main__":
    # Python 示例
    python_code = """
for i in range(5):
    print(f"Python: {i}")
"""

    # JavaScript 示例
    js_code = """
for (let i = 0; i < 5; i++) {
    console.log(`JavaScript: ${i}`);
}
"""

    # C++ 示例
    cpp_code = """
#include <iostream>
using namespace std;

int main() {
    for (int i = 0; i < 5; i++) {
        cout << "C++: " << i << endl;
    }
    return 0;
}
"""

    print("支持的语言:", get_supported_languages())
    print()

    # 测试各种语言
    for name, code in [("Python", python_code), ("JavaScript", js_code), ("C++", cpp_code)]:
        print(f"测试 {name}:")
        success, output, lang = execute_code_multi_language(code)
        print(f"语言: {lang.value}")
        print(f"成功: {success}")
        print(f"输出:\n{output}")
        print("-" * 60)
