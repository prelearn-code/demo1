"""错误修复规则库模块"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import re
import json

from ..agent.errors import ErrorType, StructuredError, ReflectionEntry


@dataclass
class CorrectionRule:
    """错误修复规则"""
    rule_id: str
    error_type: ErrorType
    pattern: str              # 错误模式（正则）
    diagnosis: str            # 诊断
    fix_template: str         # 修复模板
    confidence: float         # 置信度
    success_count: int = 0    # 成功次数
    total_count: int = 0      # 总使用次数

    @property
    def success_rate(self) -> float:
        """修复成功率"""
        if self.total_count == 0:
            return 0.0
        return self.success_count / self.total_count

    def matches(self, error_message: str) -> bool:
        """检查是否匹配此规则"""
        return re.search(self.pattern, error_message, re.IGNORECASE) is not None

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "rule_id": self.rule_id,
            "error_type": self.error_type.value,
            "pattern": self.pattern,
            "diagnosis": self.diagnosis,
            "fix_template": self.fix_template,
            "confidence": self.confidence,
            "success_count": self.success_count,
            "total_count": self.total_count
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'CorrectionRule':
        """从字典创建"""
        return cls(
            rule_id=data["rule_id"],
            error_type=ErrorType(data["error_type"]),
            pattern=data["pattern"],
            diagnosis=data["diagnosis"],
            fix_template=data["fix_template"],
            confidence=data["confidence"],
            success_count=data.get("success_count", 0),
            total_count=data.get("total_count", 0)
        )


class RuleBase:
    """规则库"""

    def __init__(self):
        self.rules: List[CorrectionRule] = []
        self._init_builtin_rules()

    def _init_builtin_rules(self):
        """初始化内置规则"""
        # 规则 1: 缺少导入
        self.add_rule(CorrectionRule(
            rule_id="IMPORT_MISSING",
            error_type=ErrorType.IMPORT,
            pattern=r"name '(\w+)' is not defined",
            diagnosis="缺少模块导入",
            fix_template="在代码开头添加: import {module}",
            confidence=0.9
        ))

        # 规则 2: 模块未找到
        self.add_rule(CorrectionRule(
            rule_id="IMPORT_MODULE_NOT_FOUND",
            error_type=ErrorType.IMPORT,
            pattern=r"ModuleNotFoundError: No module named '(\w+)'",
            diagnosis="模块未安装或不存在",
            fix_template="检查模块名是否正确，或使用标准库替代",
            confidence=0.85
        ))

        # 规则 3: 语法错误 - 缺少冒号
        self.add_rule(CorrectionRule(
            rule_id="SYNTAX_MISSING_COLON",
            error_type=ErrorType.SYNTAX,
            pattern=r"invalid syntax.*expected ':'",
            diagnosis="函数/循环定义缺少冒号",
            fix_template="在 def/for/if/while 行末添加冒号",
            confidence=0.95
        ))

        # 规则 4: 缩进错误
        self.add_rule(CorrectionRule(
            rule_id="SYNTAX_INDENTATION",
            error_type=ErrorType.SYNTAX,
            pattern=r"IndentationError|unexpected indent",
            diagnosis="缩进不正确",
            fix_template="检查并统一使用 4 个空格缩进",
            confidence=0.85
        ))

        # 规则 5: 除零错误
        self.add_rule(CorrectionRule(
            rule_id="RUNTIME_DIVISION_BY_ZERO",
            error_type=ErrorType.RUNTIME,
            pattern=r"(division by zero|ZeroDivisionError)",
            diagnosis="除数为零",
            fix_template="在除法前添加: if denominator != 0:",
            confidence=0.9
        ))

        # 规则 6: 索引越界
        self.add_rule(CorrectionRule(
            rule_id="RUNTIME_INDEX_ERROR",
            error_type=ErrorType.RUNTIME,
            pattern=r"IndexError.*out of range",
            diagnosis="列表索引越界",
            fix_template="检查索引范围，使用 if i < len(list):",
            confidence=0.85
        ))

        # 规则 7: 类型错误
        self.add_rule(CorrectionRule(
            rule_id="RUNTIME_TYPE_ERROR",
            error_type=ErrorType.RUNTIME,
            pattern=r"TypeError",
            diagnosis="类型不匹配",
            fix_template="检查变量类型，必要时进行类型转换",
            confidence=0.75
        ))

        # 规则 8: 键不存在
        self.add_rule(CorrectionRule(
            rule_id="RUNTIME_KEY_ERROR",
            error_type=ErrorType.RUNTIME,
            pattern=r"KeyError",
            diagnosis="字典键不存在",
            fix_template="使用 dict.get(key, default) 或检查 key in dict",
            confidence=0.85
        ))

    def add_rule(self, rule: CorrectionRule):
        """添加规则"""
        self.rules.append(rule)

    def match(self, error: StructuredError) -> List[CorrectionRule]:
        """
        匹配适用的规则

        Args:
            error: 结构化错误对象

        Returns:
            匹配的规则列表，按置信度排序
        """
        matches = []
        for rule in self.rules:
            if rule.error_type == error.error_type:
                if rule.matches(error.message):
                    matches.append(rule)

        # 按置信度排序
        return sorted(matches, key=lambda r: r.confidence, reverse=True)

    def learn_from_success(
        self,
        error: StructuredError,
        reflection: ReflectionEntry,
        success: bool
    ):
        """
        从成功/失败中学习

        Args:
            error: 错误对象
            reflection: 反思记录
            success: 是否成功修复
        """
        # 尝试匹配现有规则
        matched = self.match(error)

        if matched:
            # 更新统计
            rule = matched[0]
            rule.total_count += 1
            if success:
                rule.success_count += 1
        else:
            # 提取新规则（简化版）
            new_rule = self._extract_rule(error, reflection)
            if new_rule:
                self.add_rule(new_rule)

    def _extract_rule(
        self,
        error: StructuredError,
        reflection: ReflectionEntry
    ) -> Optional[CorrectionRule]:
        """
        从反思中提取新规则（启发式）

        Args:
            error: 错误对象
            reflection: 反思记录

        Returns:
            新的修复规则，如果无法提取则返回 None
        """
        # 这是一个简化版本
        # 实际可以用 LLM 辅助提取规则

        if not reflection.diagnosis or not reflection.correction_strategy:
            return None

        return CorrectionRule(
            rule_id=f"LEARNED_{len(self.rules)}",
            error_type=error.error_type,
            pattern=re.escape(error.message[:50]),  # 简化的模式
            diagnosis=reflection.diagnosis,
            fix_template=reflection.correction_strategy,
            confidence=0.5  # 初始置信度较低
        )

    def get_top_rules(self, n: int = 10) -> List[CorrectionRule]:
        """
        获取最有效的规则

        Args:
            n: 返回的规则数量

        Returns:
            最有效的规则列表
        """
        return sorted(
            self.rules,
            key=lambda r: (r.success_rate, r.total_count),
            reverse=True
        )[:n]

    def save(self, filepath: str):
        """
        保存规则库到文件

        Args:
            filepath: 保存路径
        """
        data = {
            "rules": [rule.to_dict() for rule in self.rules]
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self, filepath: str):
        """
        从文件加载规则库

        Args:
            filepath: 文件路径
        """
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)

        self.rules.clear()
        for rule_data in data["rules"]:
            rule = CorrectionRule.from_dict(rule_data)
            self.add_rule(rule)

    def get_statistics(self) -> Dict:
        """获取规则库统计信息"""
        total_rules = len(self.rules)
        used_rules = sum(1 for r in self.rules if r.total_count > 0)
        total_applications = sum(r.total_count for r in self.rules)
        total_successes = sum(r.success_count for r in self.rules)

        return {
            "total_rules": total_rules,
            "used_rules": used_rules,
            "total_applications": total_applications,
            "total_successes": total_successes,
            "overall_success_rate": total_successes / total_applications if total_applications > 0 else 0.0,
            "top_rules": [
                {
                    "rule_id": r.rule_id,
                    "success_rate": r.success_rate,
                    "applications": r.total_count
                }
                for r in self.get_top_rules(5)
            ]
        }
