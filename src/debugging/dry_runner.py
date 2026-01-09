"""轻量级执行追踪模块"""

import ast
from typing import Dict, Any, List, Union


class DryRunner:
    """轻量级执行追踪器"""

    def trace_execution(
        self,
        code: str,
        test_input: Dict[str, Any]
    ) -> List[Dict]:
        """
        追踪代码执行路径

        Args:
            code: 源代码
            test_input: 测试输入 {"x": 5, "y": 10}

        Returns:
            执行轨迹 [{"line": 3, "var": "x", "value": 7}, ...]
        """
        try:
            tree = ast.parse(code)
            tracer = ExecutionTracer(test_input)
            tracer.visit(tree)
            return tracer.trace
        except Exception as e:
            return [{"error": str(e), "type": "parse_error"}]


class ExecutionTracer(ast.NodeVisitor):
    """AST 遍历器"""

    def __init__(self, inputs: Dict):
        self.trace = []
        self.env = inputs.copy()  # 模拟环境
        self.line_number = 0

    def visit_Assign(self, node):
        """访问赋值语句"""
        try:
            # 简化：只处理简单赋值
            if isinstance(node.targets[0], ast.Name):
                var_name = node.targets[0].id

                # 尝试求值（有限支持）
                value = self._eval_expr(node.value)

                self.env[var_name] = value
                self.trace.append({
                    "line": node.lineno,
                    "type": "assign",
                    "var": var_name,
                    "value": value
                })
            elif isinstance(node.targets[0], ast.Tuple):
                # 处理多重赋值 a, b = 1, 2
                if isinstance(node.value, ast.Tuple):
                    for target, value_node in zip(node.targets[0].elts, node.value.elts):
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            value = self._eval_expr(value_node)
                            self.env[var_name] = value
                            self.trace.append({
                                "line": node.lineno,
                                "type": "assign",
                                "var": var_name,
                                "value": value
                            })
        except Exception as e:
            self.trace.append({
                "line": node.lineno,
                "type": "error",
                "message": f"Failed to trace assignment: {str(e)}"
            })

        self.generic_visit(node)

    def visit_AugAssign(self, node):
        """访问增强赋值语句 (+=, -=, etc.)"""
        try:
            if isinstance(node.target, ast.Name):
                var_name = node.target.id
                current_value = self.env.get(var_name, "???")
                increment = self._eval_expr(node.value)

                # 计算新值
                if isinstance(node.op, ast.Add):
                    new_value = current_value + increment if current_value != "???" else "???"
                elif isinstance(node.op, ast.Sub):
                    new_value = current_value - increment if current_value != "???" else "???"
                elif isinstance(node.op, ast.Mult):
                    new_value = current_value * increment if current_value != "???" else "???"
                elif isinstance(node.op, ast.Div):
                    new_value = current_value / increment if current_value != "???" and increment != 0 else "???"
                else:
                    new_value = "COMPLEX_OP"

                self.env[var_name] = new_value
                self.trace.append({
                    "line": node.lineno,
                    "type": "augassign",
                    "var": var_name,
                    "old_value": current_value,
                    "new_value": new_value
                })
        except:
            pass

        self.generic_visit(node)

    def visit_Return(self, node):
        """访问返回语句"""
        try:
            value = self._eval_expr(node.value) if node.value else None
            self.trace.append({
                "line": node.lineno,
                "type": "return",
                "value": value
            })
        except Exception as e:
            self.trace.append({
                "line": node.lineno,
                "type": "return",
                "value": f"ERROR: {str(e)}"
            })

        self.generic_visit(node)

    def visit_If(self, node):
        """访问 if 语句"""
        try:
            condition = self._eval_expr(node.test)
            self.trace.append({
                "line": node.lineno,
                "type": "condition",
                "condition": ast.unparse(node.test) if hasattr(ast, 'unparse') else "???",
                "result": condition
            })
        except:
            pass

        self.generic_visit(node)

    def visit_For(self, node):
        """访问 for 循环"""
        try:
            iter_expr = self._eval_expr(node.iter)
            self.trace.append({
                "line": node.lineno,
                "type": "loop",
                "loop_type": "for",
                "iterator": iter_expr
            })
        except:
            pass

        self.generic_visit(node)

    def visit_While(self, node):
        """访问 while 循环"""
        try:
            self.trace.append({
                "line": node.lineno,
                "type": "loop",
                "loop_type": "while",
                "condition": ast.unparse(node.test) if hasattr(ast, 'unparse') else "???"
            })
        except:
            pass

        self.generic_visit(node)

    def _eval_expr(self, node) -> Union[int, float, str, list, bool]:
        """求值表达式（简化版）"""
        if node is None:
            return None

        if isinstance(node, ast.Constant):
            return node.value

        elif isinstance(node, ast.Name):
            return self.env.get(node.id, "???")

        elif isinstance(node, ast.BinOp):
            left = self._eval_expr(node.left)
            right = self._eval_expr(node.right)

            if left == "???" or right == "???":
                return "???"

            try:
                if isinstance(node.op, ast.Add):
                    return left + right
                elif isinstance(node.op, ast.Sub):
                    return left - right
                elif isinstance(node.op, ast.Mult):
                    return left * right
                elif isinstance(node.op, ast.Div):
                    if right == 0:
                        return "DIVISION_BY_ZERO"
                    return left / right
                elif isinstance(node.op, ast.FloorDiv):
                    if right == 0:
                        return "DIVISION_BY_ZERO"
                    return left // right
                elif isinstance(node.op, ast.Mod):
                    return left % right
                elif isinstance(node.op, ast.Pow):
                    return left ** right
            except:
                return "EVAL_ERROR"

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_expr(node.operand)
            if operand == "???":
                return "???"

            try:
                if isinstance(node.op, ast.USub):
                    return -operand
                elif isinstance(node.op, ast.UAdd):
                    return +operand
                elif isinstance(node.op, ast.Not):
                    return not operand
            except:
                return "EVAL_ERROR"

        elif isinstance(node, ast.Compare):
            left = self._eval_expr(node.left)
            if len(node.ops) == 1 and len(node.comparators) == 1:
                right = self._eval_expr(node.comparators[0])
                op = node.ops[0]

                if left == "???" or right == "???":
                    return "???"

                try:
                    if isinstance(op, ast.Eq):
                        return left == right
                    elif isinstance(op, ast.NotEq):
                        return left != right
                    elif isinstance(op, ast.Lt):
                        return left < right
                    elif isinstance(op, ast.LtE):
                        return left <= right
                    elif isinstance(op, ast.Gt):
                        return left > right
                    elif isinstance(op, ast.GtE):
                        return left >= right
                except:
                    return "EVAL_ERROR"

        elif isinstance(node, ast.List):
            return [self._eval_expr(elt) for elt in node.elts]

        elif isinstance(node, ast.Tuple):
            return tuple(self._eval_expr(elt) for elt in node.elts)

        elif isinstance(node, ast.Call):
            # 处理一些简单的内置函数
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name == "range" and len(node.args) > 0:
                    args = [self._eval_expr(arg) for arg in node.args]
                    if all(isinstance(a, int) for a in args):
                        return list(range(*args))
                elif func_name == "len" and len(node.args) == 1:
                    arg = self._eval_expr(node.args[0])
                    if isinstance(arg, (list, str, tuple)):
                        return len(arg)

        return "COMPLEX_EXPR"


def format_trace(trace: List[Dict]) -> str:
    """
    格式化追踪结果

    Args:
        trace: 追踪记录列表

    Returns:
        格式化的字符串
    """
    lines = []
    for step in trace:
        step_type = step.get("type")

        if step_type == "assign":
            lines.append(
                f"第 {step['line']} 行: {step['var']} = {step['value']}"
            )
        elif step_type == "augassign":
            lines.append(
                f"第 {step['line']} 行: {step['var']} 从 {step['old_value']} 变为 {step['new_value']}"
            )
        elif step_type == "return":
            lines.append(
                f"第 {step['line']} 行: 返回 {step['value']}"
            )
        elif step_type == "condition":
            lines.append(
                f"第 {step['line']} 行: 条件 {step.get('condition', '???')} = {step['result']}"
            )
        elif step_type == "loop":
            if step['loop_type'] == "for":
                lines.append(
                    f"第 {step['line']} 行: for 循环，迭代 {step.get('iterator', '???')}"
                )
            else:
                lines.append(
                    f"第 {step['line']} 行: while 循环，条件: {step.get('condition', '???')}"
                )
        elif step_type == "error":
            lines.append(
                f"第 {step['line']} 行: 错误 - {step['message']}"
            )

    return "\n".join(lines) if lines else "无追踪记录"
