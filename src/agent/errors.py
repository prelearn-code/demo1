"""错误表示和解析模块"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
import re


class ErrorType(Enum):
    """错误类型枚举"""
    SYNTAX = "syntax"          # 语法错误
    IMPORT = "import"          # 导入错误
    RUNTIME = "runtime"        # 运行时错误
    LOGIC = "logic"            # 逻辑错误（输出不匹配）
    TIMEOUT = "timeout"        # 超时错误
    UNKNOWN = "unknown"        # 未知错误


@dataclass
class StructuredError:
    """结构化错误表示"""
    error_type: ErrorType
    message: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    context: Dict[str, Any] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "error_type": self.error_type.value,
            "message": self.message,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "context": self.context
        }

    def __str__(self) -> str:
        """字符串表示"""
        parts = [f"[{self.error_type.value.upper()}] {self.message}"]
        if self.line_number:
            parts.append(f"Line {self.line_number}")
        if self.code_snippet:
            parts.append(f"Code: {self.code_snippet}")
        return " | ".join(parts)


@dataclass
class ReflectionEntry:
    """反思记录"""
    iteration: int
    error: StructuredError
    diagnosis: str              # 诊断结果
    correction_strategy: str    # 修正策略
    corrected_code: str        # 修正后的代码
    success: bool              # 是否成功

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "iteration": self.iteration,
            "error": self.error.to_dict(),
            "diagnosis": self.diagnosis,
            "correction_strategy": self.correction_strategy,
            "corrected_code": self.corrected_code,
            "success": self.success
        }


class ErrorParser:
    """错误解析器：将 stderr 转换为 StructuredError"""

    # 错误模式匹配规则
    PATTERNS = {
        ErrorType.SYNTAX: [
            r"SyntaxError:",
            r"invalid syntax",
            r"unexpected EOF",
            r"IndentationError:",
            r"TabError:"
        ],
        ErrorType.IMPORT: [
            r"ModuleNotFoundError:",
            r"ImportError:",
            r"name '(\w+)' is not defined"
        ],
        ErrorType.RUNTIME: [
            r"TypeError:",
            r"ValueError:",
            r"AttributeError:",
            r"KeyError:",
            r"IndexError:",
            r"ZeroDivisionError:",
            r"NameError:",
        ],
        ErrorType.TIMEOUT: [
            r"TimeoutError",
            r"timeout",
            r"timed out"
        ]
    }

    @classmethod
    def parse(cls, stderr: str, code: str = "") -> StructuredError:
        """
        解析错误信息

        Args:
            stderr: 标准错误输出
            code: 源代码（用于提取上下文）

        Returns:
            StructuredError 对象
        """
        if not stderr or stderr.strip() == "":
            # 没有错误，可能是逻辑错误
            return StructuredError(
                error_type=ErrorType.LOGIC,
                message="No error output, possible logic error"
            )

        # 识别错误类型
        error_type = cls._identify_error_type(stderr)

        # 提取行号
        line_number = cls._extract_line_number(stderr)

        # 提取错误消息
        message = cls._extract_message(stderr)

        # 提取代码片段
        code_snippet = None
        if line_number and code:
            code_snippet = cls._extract_code_snippet(code, line_number)

        return StructuredError(
            error_type=error_type,
            message=message,
            line_number=line_number,
            code_snippet=code_snippet,
            context={"raw_stderr": stderr}
        )

    @classmethod
    def _identify_error_type(cls, stderr: str) -> ErrorType:
        """识别错误类型"""
        for error_type, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, stderr, re.IGNORECASE):
                    return error_type
        return ErrorType.UNKNOWN

    @classmethod
    def _extract_line_number(cls, stderr: str) -> Optional[int]:
        """提取行号"""
        # 尝试匹配常见的行号格式
        patterns = [
            r'line (\d+)',
            r'File ".*", line (\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, stderr, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    @classmethod
    def _extract_message(cls, stderr: str) -> str:
        """提取主要错误消息"""
        lines = stderr.strip().split('\n')

        # 通常最后一行包含主要错误信息
        for line in reversed(lines):
            line = line.strip()
            if line and not line.startswith(' '):
                return line

        # 如果没找到，返回整个stderr的摘要
        return stderr.strip()[:200]

    @classmethod
    def _extract_code_snippet(cls, code: str, line_number: int) -> Optional[str]:
        """提取错误行的代码片段"""
        try:
            lines = code.split('\n')
            if 1 <= line_number <= len(lines):
                return lines[line_number - 1].strip()
        except:
            pass
        return None
