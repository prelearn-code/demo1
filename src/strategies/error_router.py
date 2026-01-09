"""错误路由器：根据错误类型使用不同的修复策略"""

from typing import Dict, Callable, Optional
import re

from ..agent.errors import ErrorType, StructuredError
from ..agent.state import AgentState
from ..learning.rule_base import RuleBase
from ..debugging.dry_runner import DryRunner, format_trace


class ErrorRouter:
    """错误类型路由器"""

    def __init__(self, rule_base: Optional[RuleBase] = None):
        """
        初始化路由器

        Args:
            rule_base: 规则库实例，如果未提供则创建新实例
        """
        self.rule_base = rule_base or RuleBase()
        self.dry_runner = DryRunner()

        self.strategies: Dict[ErrorType, Callable] = {
            ErrorType.SYNTAX: self.handle_syntax_error,
            ErrorType.IMPORT: self.handle_import_error,
            ErrorType.RUNTIME: self.handle_runtime_error,
            ErrorType.LOGIC: self.handle_logic_error,
            ErrorType.TIMEOUT: self.handle_timeout_error,
            ErrorType.UNKNOWN: self.handle_unknown_error
        }

    def route(self, state: AgentState) -> Dict[str, str]:
        """
        根据错误类型路由到特定策略

        Args:
            state: Agent 状态

        Returns:
            包含路由结果的字典，可能包含：
            - strategy: 使用的策略名称
            - auto_fixed: 自动修复的代码（如果适用）
            - suggestion: 修复建议
            - trace: 执行追踪（如果适用）
        """
        error = state.get("structured_error")
        if not error:
            return {"strategy": "none", "message": "No error to route"}

        if error.error_type in self.strategies:
            handler = self.strategies[error.error_type]
            return handler(state, error)

        # 默认策略
        return self.default_strategy(state, error)

    def handle_syntax_error(self, state: AgentState, error: StructuredError) -> Dict:
        """语法错误：高置信度，快速修复"""
        result = {
            "strategy": "syntax_rule_based",
            "error_type": "syntax"
        }

        # 1. 尝试规则匹配
        rules = self.rule_base.match(error)
        if rules and rules[0].confidence > 0.8:
            # 高置信度规则
            best_rule = rules[0]
            result["matched_rule"] = best_rule.rule_id
            result["confidence"] = best_rule.confidence
            result["suggestion"] = best_rule.fix_template
            result["diagnosis"] = best_rule.diagnosis

            print(f"[Router] 语法错误 → 使用规则: {best_rule.rule_id}")
            print(f"[Router] 置信度: {best_rule.confidence:.2f}")
            print(f"[Router] 建议: {best_rule.fix_template}")
        else:
            result["suggestion"] = "需要 LLM 反思分析语法错误"
            print("[Router] 语法错误 → 未找到高置信度规则，使用标准反思")

        return result

    def handle_import_error(self, state: AgentState, error: StructuredError) -> Dict:
        """导入错误：提取模块名，直接添加或提供建议"""
        result = {
            "strategy": "import_auto_fix",
            "error_type": "import"
        }

        print("[Router] 导入错误 → 尝试自动修复")

        # 提取缺失的模块名
        match = re.search(r"name '(\w+)' is not defined", error.message)

        if match:
            module = match.group(1)
            code = state.get("code", "")

            # 检查是否已经导入
            if f"import {module}" not in code:
                # 自动生成修复建议
                result["missing_module"] = module
                result["suggestion"] = f"在代码开头添加: import {module}"
                result["auto_fix_available"] = True

                print(f"[Router] 检测到缺失模块: {module}")
                print(f"[Router] 建议: import {module}")
            else:
                result["suggestion"] = f"模块 {module} 已导入，但可能是作用域问题"
        else:
            # ModuleNotFoundError
            match = re.search(r"No module named '(\w+)'", error.message)
            if match:
                module = match.group(1)
                result["missing_module"] = module
                result["suggestion"] = f"模块 {module} 不存在，可能需要安装或使用标准库替代"
                result["auto_fix_available"] = False
                print(f"[Router] 模块 {module} 未安装")

        return result

    def handle_runtime_error(self, state: AgentState, error: StructuredError) -> Dict:
        """运行时错误：标准反思流程 + 规则建议"""
        result = {
            "strategy": "runtime_standard",
            "error_type": "runtime"
        }

        print("[Router] 运行时错误 → 标准反思流程")

        # 尝试匹配规则
        rules = self.rule_base.match(error)
        if rules:
            best_rule = rules[0]
            result["matched_rule"] = best_rule.rule_id
            result["suggestion"] = best_rule.fix_template
            result["diagnosis"] = best_rule.diagnosis
            print(f"[Router] 匹配到规则: {best_rule.rule_id}")
            print(f"[Router] 建议: {best_rule.fix_template}")
        else:
            result["suggestion"] = "需要详细分析运行时错误的原因"

        return result

    def handle_logic_error(self, state: AgentState, error: StructuredError) -> Dict:
        """逻辑错误：启用 dry run 执行追踪"""
        result = {
            "strategy": "logic_with_trace",
            "error_type": "logic"
        }

        print("[Router] 逻辑错误 → 启用执行追踪")

        code = state.get("code", "")

        # 尝试从状态中获取测试输入
        test_input = state.get("test_input", {})

        if not test_input:
            # 使用默认测试输入
            result["trace"] = "无法执行追踪：缺少测试输入"
            result["suggestion"] = "分析输出不匹配的原因，检查算法逻辑"
        else:
            # 执行 dry run
            try:
                trace = self.dry_runner.trace_execution(code, test_input)
                trace_str = format_trace(trace)

                result["trace"] = trace_str
                result["suggestion"] = f"执行追踪显示：\n{trace_str}\n\n请根据追踪结果分析逻辑错误"

                print("[Router] 执行追踪完成")
                print(f"[Router] 追踪步数: {len(trace)}")
            except Exception as e:
                result["trace"] = f"追踪失败: {str(e)}"
                result["suggestion"] = "无法生成执行追踪，需要手动分析"

        return result

    def handle_timeout_error(self, state: AgentState, error: StructuredError) -> Dict:
        """超时错误：分析复杂度"""
        result = {
            "strategy": "timeout_complexity",
            "error_type": "timeout"
        }

        print("[Router] 超时错误 → 分析算法复杂度")

        result["suggestion"] = """代码执行超时，请分析：
1. 算法时间复杂度是否过高（如 O(n²) 或更高）
2. 是否存在无限循环
3. 是否可以优化数据结构或算法
4. 考虑使用更高效的方法（如动态规划、贪心等）"""

        return result

    def handle_unknown_error(self, state: AgentState, error: StructuredError) -> Dict:
        """未知错误：默认处理"""
        result = {
            "strategy": "unknown_default",
            "error_type": "unknown"
        }

        print("[Router] 未知错误 → 使用默认策略")
        result["suggestion"] = "未能识别错误类型，需要仔细分析错误信息"

        return result

    def default_strategy(self, state: AgentState, error: StructuredError) -> Dict:
        """默认策略"""
        return {
            "strategy": "default",
            "suggestion": "使用标准反思流程"
        }

    def update_rule_statistics(
        self,
        error: StructuredError,
        matched_rule_id: Optional[str],
        success: bool
    ):
        """
        更新规则统计信息

        Args:
            error: 错误对象
            matched_rule_id: 匹配的规则ID
            success: 修复是否成功
        """
        if not matched_rule_id:
            return

        # 找到对应的规则并更新统计
        for rule in self.rule_base.rules:
            if rule.rule_id == matched_rule_id:
                rule.total_count += 1
                if success:
                    rule.success_count += 1
                break
