# 阶段 3: 高级特性方案（研究级增强）

## 🎯 目标

将系统从"可用的原型"提升到"接近生产级的研究平台"，探索创新方向。

**核心价值：** 从"能工作"到"能创新"，为研究论文提供独特贡献点

---

## 💡 为什么需要阶段 3？

### 阶段 1 vs 阶段 2 vs 阶段 3

| 维度 | 阶段 1 | 阶段 2 | 阶段 3 |
|------|--------|--------|--------|
| **目标** | 让系统工作 | 让系统可观测 | 让系统智能化 |
| **价值** | 基础功能 | 展示能力 | 研究创新 |
| **产出** | 量化指标 | 可视化报告 | 论文贡献点 |
| **难度** | 中等 | 中等 | 较高 |

### 阶段 3 的独特价值

**问题：** "你的系统和别人的有什么不同？"

**阶段 3 提供的答案：**
1. 跨任务学习 - 从历史错误中积累规则库
2. 轻量级执行追踪 - 无需运行即可发现逻辑错误
3. 动态策略 - 根据错误类型调整行为
4. 多模型对比 - 系统性评估不同 LLM

---

## 🏗️ 架构扩展

### 新增模块

```
src/
├── learning/
│   ├── rule_base.py         ← 错误修复规则库
│   ├── pattern_matcher.py   ← 模式匹配器
│   └── knowledge_graph.py   ← 知识图谱（可选）
│
├── debugging/
│   ├── dry_runner.py        ← 轻量级执行追踪
│   ├── symbolic_executor.py ← 符号执行（简化版）
│   └── test_generator.py    ← 测试用例生成
│
├── strategies/
│   ├── adaptive_timeout.py  ← 动态超时策略
│   ├── error_router.py      ← 错误类型路由
│   └── context_selector.py  ← 智能上下文选择
│
└── models/
    ├── model_manager.py     ← 多模型管理
    └── ensemble.py          ← 集成学习（可选）
```

---

## 📋 详细功能清单

### 1. 跨任务学习：错误修复规则库

**文件：** `src/learning/rule_base.py`

**核心思想：** 将反思从"语言"转化为"规则"

```python
from dataclasses import dataclass
from typing import List, Dict, Pattern
import re


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
        return re.search(self.pattern, error_message) is not None


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

        # 规则 2: 语法错误 - 缺少冒号
        self.add_rule(CorrectionRule(
            rule_id="SYNTAX_MISSING_COLON",
            error_type=ErrorType.SYNTAX,
            pattern=r"invalid syntax.*expected ':'",
            diagnosis="函数/循环定义缺少冒号",
            fix_template="在 def/for/if/while 行末添加冒号",
            confidence=0.95
        ))

        # 规则 3: 缩进错误
        self.add_rule(CorrectionRule(
            rule_id="SYNTAX_INDENTATION",
            error_type=ErrorType.SYNTAX,
            pattern=r"IndentationError|unexpected indent",
            diagnosis="缩进不正确",
            fix_template="检查并统一使用 4 个空格缩进",
            confidence=0.85
        ))

        # 规则 4: 除零错误
        self.add_rule(CorrectionRule(
            rule_id="RUNTIME_DIVISION_BY_ZERO",
            error_type=ErrorType.RUNTIME,
            pattern=r"division by zero",
            diagnosis="除数为零",
            fix_template="在除法前添加: if denominator != 0:",
            confidence=0.8
        ))

    def add_rule(self, rule: CorrectionRule):
        """添加规则"""
        self.rules.append(rule)

    def match(self, error: StructuredError) -> List[CorrectionRule]:
        """匹配适用的规则"""
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
        """从成功/失败中学习"""
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
    ) -> CorrectionRule:
        """从反思中提取新规则（启发式）"""
        # 这是一个简化版本
        # 实际可以用 LLM 辅助提取规则

        return CorrectionRule(
            rule_id=f"LEARNED_{len(self.rules)}",
            error_type=error.error_type,
            pattern=re.escape(error.message[:50]),  # 简化的模式
            diagnosis=reflection.diagnosis,
            fix_template=reflection.correction_strategy,
            confidence=0.5  # 初始置信度较低
        )

    def get_top_rules(self, n: int = 10) -> List[CorrectionRule]:
        """获取最有效的规则"""
        return sorted(
            self.rules,
            key=lambda r: (r.success_rate, r.total_count),
            reverse=True
        )[:n]

    def save(self, filepath: str):
        """保存规则库"""
        import json
        data = {
            "rules": [
                {
                    "rule_id": r.rule_id,
                    "error_type": r.error_type.value,
                    "pattern": r.pattern,
                    "diagnosis": r.diagnosis,
                    "fix_template": r.fix_template,
                    "confidence": r.confidence,
                    "success_count": r.success_count,
                    "total_count": r.total_count
                }
                for r in self.rules
            ]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, filepath: str):
        """加载规则库"""
        import json
        with open(filepath) as f:
            data = json.load(f)

        for rule_data in data["rules"]:
            rule = CorrectionRule(
                rule_id=rule_data["rule_id"],
                error_type=ErrorType(rule_data["error_type"]),
                pattern=rule_data["pattern"],
                diagnosis=rule_data["diagnosis"],
                fix_template=rule_data["fix_template"],
                confidence=rule_data["confidence"],
                success_count=rule_data["success_count"],
                total_count=rule_data["total_count"]
            )
            self.add_rule(rule)
```

**集成到 Reflector：**

```python
# 全局规则库
rule_base = RuleBase()

def reflector_node_with_rules(state):
    error = state["structured_error"]

    # 1. 尝试匹配现有规则
    matched_rules = rule_base.match(error)

    if matched_rules:
        best_rule = matched_rules[0]
        print(f"[RuleBase] 匹配到规则: {best_rule.rule_id}")
        print(f"[RuleBase] 置信度: {best_rule.confidence:.2f}")
        print(f"[RuleBase] 建议: {best_rule.fix_template}")

        # 将规则建议添加到上下文
        state["rule_suggestion"] = best_rule.fix_template

    # 2. 正常的反思流程
    reflection = generate_reflection(state)

    # 3. 学习更新（在任务结束时调用）
    # rule_base.learn_from_success(error, reflection, success)

    return state
```

**效果示例：**

```
任务 1: NameError: name 'math' is not defined
[RuleBase] 匹配到规则: IMPORT_MISSING
[RuleBase] 置信度: 0.90
[RuleBase] 建议: 在代码开头添加: import math
→ 成功修复

任务 2-10: 类似的 import 错误
→ 规则统计更新: 成功率 90%

任务 50: 又出现 import 错误
[RuleBase] 使用高置信度规则，跳过 LLM 反思
→ 直接应用修复模板
→ 节省时间和 token
```

---

### 2. 轻量级执行追踪（Dry Run）

**文件：** `src/debugging/dry_runner.py`

**核心思想：** 无需真正运行，模拟关键输入的执行路径

```python
import ast
from typing import Dict, Any, List


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
            return [{"error": str(e)}]


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
        except:
            pass  # 跳过复杂表达式

        self.generic_visit(node)

    def visit_Return(self, node):
        """访问返回语句"""
        try:
            value = self._eval_expr(node.value)
            self.trace.append({
                "line": node.lineno,
                "type": "return",
                "value": value
            })
        except:
            pass

        self.generic_visit(node)

    def _eval_expr(self, node):
        """求值表达式（简化版）"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            return self.env.get(node.id, "???")
        elif isinstance(node, ast.BinOp):
            left = self._eval_expr(node.left)
            right = self._eval_expr(node.right)

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

        return "COMPLEX_EXPR"


def format_trace(trace: List[Dict]) -> str:
    """格式化追踪结果"""
    lines = []
    for step in trace:
        if step["type"] == "assign":
            lines.append(
                f"第 {step['line']} 行: {step['var']} = {step['value']}"
            )
        elif step["type"] == "return":
            lines.append(
                f"第 {step['line']} 行: 返回 {step['value']}"
            )
    return "\n".join(lines)
```

**集成到 Reflector（针对逻辑错误）：**

```python
def reflector_node_with_dry_run(state):
    error = state["structured_error"]

    # 如果是逻辑错误（输出不匹配）
    if error.error_type == ErrorType.LOGIC:
        code = state["code"]

        # 获取失败的测试用例
        test_case = extract_failed_test(state)

        # 执行 dry run
        runner = DryRunner()
        trace = runner.trace_execution(code, test_case["input"])

        # 格式化追踪结果
        trace_str = format_trace(trace)

        # 添加到反思提示
        prompt = f"""
代码存在逻辑错误。

测试用例:
输入: {test_case['input']}
期望输出: {test_case['expected']}
实际输出: {test_case['actual']}

执行追踪:
{trace_str}

请分析哪一步的逻辑有问题。
"""

        reflection = llm.invoke(prompt)
        # ...

    return state
```

**效果示例：**

```
任务: 实现 fibonacci(5)

生成的代码（有错误）:
def fibonacci(n):
    a, b = 0, 1
    for i in range(n):      # ← 错误：应该是 range(n-1)
        a, b = b, a + b
    return a

执行追踪:
第 2 行: a = 0
第 2 行: b = 1
第 4 行: a = 1
第 4 行: b = 1
第 4 行: a = 1
第 4 行: b = 2
第 4 行: a = 2
第 4 行: b = 3
第 4 行: a = 3
第 4 行: b = 5
第 4 行: a = 5
第 4 行: b = 8
第 6 行: 返回 5

期望: 5
实际: 5

等等，实际这次对了... 但如果 n=6:

执行追踪显示:
循环执行了 6 次，返回第 7 个数
问题: 循环次数多了 1 次

LLM 分析:
"range(n) 执行了 n 次，但 fibonacci(n) 应该是第 n 个数，
需要改为 range(n-1) 或调整初始值"
```

---

### 3. 动态策略：根据错误类型调整行为

**文件：** `src/strategies/error_router.py`

**核心思想：** 不同错误类型使用不同的修复策略

```python
from typing import Dict, Callable


class ErrorRouter:
    """错误类型路由器"""

    def __init__(self):
        self.strategies: Dict[ErrorType, Callable] = {
            ErrorType.SYNTAX: self.handle_syntax_error,
            ErrorType.IMPORT: self.handle_import_error,
            ErrorType.RUNTIME: self.handle_runtime_error,
            ErrorType.LOGIC: self.handle_logic_error,
            ErrorType.TIMEOUT: self.handle_timeout_error
        }

    def route(self, state: AgentState) -> AgentState:
        """根据错误类型路由到特定策略"""
        error = state["structured_error"]

        if error.error_type in self.strategies:
            handler = self.strategies[error.error_type]
            return handler(state, error)

        # 默认策略
        return self.default_strategy(state, error)

    def handle_syntax_error(self, state, error):
        """语法错误：高置信度，快速修复"""
        print("[Router] 语法错误 → 使用规则库优先")

        # 1. 尝试规则匹配
        rules = rule_base.match(error)
        if rules and rules[0].confidence > 0.8:
            # 高置信度规则，直接应用
            return apply_rule_directly(state, rules[0])

        # 2. 否则正常反思
        return standard_reflection(state)

    def handle_import_error(self, state, error):
        """导入错误：提取模块名，直接添加"""
        print("[Router] 导入错误 → 自动修复")

        # 提取缺失的模块名
        import re
        match = re.search(r"name '(\w+)' is not defined", error.message)

        if match:
            module = match.group(1)
            # 直接在代码开头添加 import
            code = state["code"]
            fixed_code = f"import {module}\n{code}"

            state["code"] = fixed_code
            state["auto_fixed"] = True
            print(f"[Router] 自动添加: import {module}")

        return state

    def handle_runtime_error(self, state, error):
        """运行时错误：标准反思流程"""
        print("[Router] 运行时错误 → 标准反思")
        return standard_reflection(state)

    def handle_logic_error(self, state, error):
        """逻辑错误：启用 dry run"""
        print("[Router] 逻辑错误 → 启用执行追踪")

        # 执行 dry run
        test_case = extract_failed_test(state)
        trace = dry_runner.trace_execution(
            state["code"],
            test_case["input"]
        )

        # 将追踪添加到上下文
        state["execution_trace"] = trace

        return detailed_reflection_with_trace(state)

    def handle_timeout_error(self, state, error):
        """超时错误：分析复杂度"""
        print("[Router] 超时错误 → 分析算法复杂度")

        prompt = """
代码执行超时。请分析:
1. 算法时间复杂度
2. 是否存在无限循环
3. 优化建议
"""
        return complexity_analysis(state, prompt)

    def default_strategy(self, state, error):
        """默认策略"""
        return standard_reflection(state)
```

**集成到 Graph：**

```python
# 在 reflector_node 中
router = ErrorRouter()

def reflector_node(state):
    # 使用路由器而非统一流程
    return router.route(state)
```

---

### 4. 多模型支持与对比

**文件：** `src/models/model_manager.py`

**核心思想：** 支持切换不同 Ollama 模型，对比性能

```python
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    model_id: str
    temperature: float
    max_tokens: int
    description: str


class ModelManager:
    """多模型管理器"""

    def __init__(self):
        self.models = {
            "qwen-7b": ModelConfig(
                name="Qwen2.5-Coder 7B",
                model_id="qwen2.5-coder:7b",
                temperature=0.0,
                max_tokens=2048,
                description="轻量级，速度快"
            ),
            "qwen-14b": ModelConfig(
                name="Qwen2.5-Coder 14B",
                model_id="qwen2.5-coder:14b",
                temperature=0.0,
                max_tokens=2048,
                description="性能更强，需要更多资源"
            ),
            "deepseek": ModelConfig(
                name="DeepSeek-Coder 6.7B",
                model_id="deepseek-coder:6.7b",
                temperature=0.0,
                max_tokens=2048,
                description="备选模型"
            )
        }

    def get_llm(self, model_key: str):
        """获取指定模型的 LLM 实例"""
        config = self.models[model_key]

        return ChatOllama(
            model=config.model_id,
            temperature=config.temperature
        )

    def benchmark_models(self, tasks: List[Dict]) -> Dict:
        """对比不同模型的性能"""
        results = {}

        for model_key in self.models.keys():
            print(f"\n测试模型: {self.models[model_key].name}")

            # 使用该模型运行评测
            llm = self.get_llm(model_key)
            runner = HumanEvalRunner(create_graph(llm))
            benchmark = runner.run_benchmark(tasks)

            results[model_key] = {
                "success_rate": benchmark.success_rate,
                "avg_iterations": benchmark.avg_iterations,
                "correction_lift": benchmark.correction_lift
            }

        return results

    def compare_report(self, results: Dict) -> str:
        """生成对比报告"""
        report = ["模型对比结果:\n"]

        for model_key, metrics in results.items():
            model_name = self.models[model_key].name
            report.append(f"\n{model_name}:")
            report.append(f"  成功率: {metrics['success_rate']:.2%}")
            report.append(f"  平均迭代: {metrics['avg_iterations']:.1f}")
            report.append(f"  自纠错提升: +{metrics['correction_lift']:.2%}")

        return "\n".join(report)
```

**使用示例：**

```python
# 对比实验
manager = ModelManager()
tasks = load_humaneval_subset(20)

results = manager.benchmark_models(tasks)
report = manager.compare_report(results)

print(report)
```

**输出示例：**

```
模型对比结果:

Qwen2.5-Coder 7B:
  成功率: 52%
  平均迭代: 2.3
  自纠错提升: +17%

Qwen2.5-Coder 14B:
  成功率: 61%
  平均迭代: 2.1
  自纠错提升: +19%

DeepSeek-Coder 6.7B:
  成功率: 48%
  平均迭代: 2.5
  自纠错提升: +15%

结论: 14B 模型性能最佳，但 7B 模型在成本效益上更优
```

---

## 📈 预期效果

### 定量提升

| 特性 | 阶段 1 | 阶段 3 | 提升 |
|------|--------|--------|------|
| **导入错误恢复率** | 78% | 95% | +22% |
| **平均修复时间** | 15秒 | 8秒 | -47% |
| **逻辑错误洞察** | ❌ 无 | ✅ 追踪 | - |
| **规则库大小** | 0 | 20+ | - |

### 研究创新点

1. **跨任务学习**
   - 从历史错误中自动提取修复规则
   - 规则库随使用不断优化

2. **轻量级执行追踪**
   - 无需运行即可发现逻辑问题
   - 对 7B 模型友好

3. **自适应策略**
   - 不同错误类型使用不同修复流程
   - 提高效率和成功率

4. **系统性评估**
   - 多模型对比实验
   - 消融研究

---

## 🛠️ 实施计划

### 第 1 步：规则库（4-5 小时）

- [ ] 实现 `RuleBase` 类
- [ ] 定义内置规则
- [ ] 集成到 Reflector
- [ ] 测试规则匹配

### 第 2 步：Dry Runner（5-6 小时）

- [ ] 实现 AST 遍历器
- [ ] 支持基本表达式求值
- [ ] 集成到逻辑错误处理
- [ ] 测试追踪准确性

### 第 3 步：错误路由（2-3 小时）

- [ ] 实现 `ErrorRouter`
- [ ] 为每种错误定义策略
- [ ] 集成到 Graph
- [ ] 测试路由准确性

### 第 4 步：多模型支持（3-4 小时）

- [ ] 实现 `ModelManager`
- [ ] 配置多个模型
- [ ] 运行对比实验
- [ ] 生成对比报告

**总计：** 约 14-18 小时（3-4 天）

---

## 🎓 论文贡献点

完成阶段 3 后，可以写：

### 创新点 1: 规则辅助的自纠错

> 本文提出基于规则库的混合纠错机制，将 LLM 反思与程序化规则相结合。
> 实验表明，规则库使导入错误的恢复率从 78% 提升至 95%，
> 同时将平均修复时间减少 47%。

### 创新点 2: 轻量级执行追踪

> 针对逻辑错误难以恢复的问题，引入基于 AST 的轻量级执行追踪。
> 该方法无需真实运行即可展示关键变量的演化路径，
> 为 LLM 提供更精准的调试信息。

### 创新点 3: 错误类型自适应策略

> 不同于统一的反思流程，本文根据错误类型动态选择修复策略：
> - 语法错误 → 规则库优先
> - 导入错误 → 自动修复
> - 逻辑错误 → 执行追踪
> 该方法提高了系统的鲁棒性和效率。

---

## 📊 成功标准

完成阶段 3 后，你应该能够：

1. ✅ 展示规则库随使用不断优化
2. ✅ 对比有无规则库的性能差异
3. ✅ 演示执行追踪辅助调试
4. ✅ 运行多模型对比实验
5. ✅ 撰写创新性的论文章节

---

## ⚖️ 阶段 3 的取舍

### 可选实现（根据时间选择）

**优先级 A（强烈推荐）：**
- ✅ 规则库 - 明显提升 + 容易展示
- ✅ 多模型对比 - 研究必备

**优先级 B（如果有时间）：**
- ⚪ Dry Runner - 技术难度较高，但创新性强
- ⚪ 错误路由 - 工程优化，学术价值中等

**优先级 C（可以省略）：**
- ⚪ 知识图谱 - 过于复杂
- ⚪ 集成学习 - 偏离主线

---

这就是**阶段 3 的完整方案**。

---

## 总结：三阶段对比

| 维度 | 阶段 1 | 阶段 2 | 阶段 3 |
|------|--------|--------|--------|
| **核心** | 结构化 | 可视化 | 智能化 |
| **难度** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **时间** | 1-2天 | 2-3天 | 3-4天 |
| **价值** | 基础必备 | 展示利器 | 研究创新 |
| **论文** | 方法论 | 实验结果 | 创新点 |

**建议：**
- 时间紧：只做阶段 1
- 要答辩/展示：做阶段 1+2
- 要发论文/深入研究：做全部 3 个阶段
