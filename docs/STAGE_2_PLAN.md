# 阶段 2: 可观测性增强方案

## 🎯 目标

让系统的执行过程**可视化、可追溯、可对比**，支持论文写作、答辩演示、博客分享。

**核心价值：** 从"能运行"到"能展示"，让别人看懂你的系统为什么有效

---

## 💡 为什么需要阶段 2？

### 场景 1: 论文答辩

**问题：** "你说自纠错有效，证据在哪？"

**有了阶段 2：**
```
打开 HTML 报告 →
- 展示完整的执行轨迹
- 对比有/无 Reflection 的差异
- 可视化错误类型分布
- 展示成功案例和失败案例
```

---

### 场景 2: 技术博客

**问题：** 如何写一篇有说服力的文章？

**有了阶段 2：**
```
自动生成:
- 精美的可视化图表
- 执行过程的动画演示
- 典型案例的逐步分析
- 对比实验的数据表格
```

---

### 场景 3: 调试优化

**问题：** 为什么某个任务失败了？

**有了阶段 2：**
```
查看轨迹记录:
- 每次迭代的完整状态
- LLM 的原始输出
- 反思的演化过程
- 决策节点的判断依据
```

---

## 🏗️ 架构扩展

### 新增模块

```
src/
├── evaluation/
│   ├── tracer.py           ← 执行轨迹记录器
│   ├── analyzer.py         ← 统计分析引擎
│   └── visualizer.py       ← 可视化生成器
│
├── reports/
│   ├── template.html       ← HTML 报告模板
│   └── generator.py        ← 报告生成器
│
└── experiments/
    ├── baseline.py         ← 基线对比实验
    ├── ablation.py         ← 消融实验
    └── runner.py           ← 实验运行器
```

---

## 📋 详细功能清单

### 1. 执行轨迹记录器

**文件：** `src/evaluation/tracer.py`

**功能：** 记录每次执行的完整信息

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class IterationTrace:
    """单次迭代的完整记录"""
    iteration: int
    timestamp: datetime

    # 输入
    input_prompt: str
    context: str  # 包含的反思记忆

    # LLM 输出
    raw_llm_output: str
    extracted_code: str

    # 执行结果
    execution_success: bool
    execution_output: str
    structured_error: Optional[StructuredError]

    # 反思
    reflection: Optional[ReflectionEntry]

    # 决策
    decision: str  # "continue" / "terminate"
    decision_reason: str


@dataclass
class TaskTrace:
    """单个任务的完整执行轨迹"""
    task_id: str
    task_prompt: str
    start_time: datetime
    end_time: datetime

    # 迭代轨迹
    iterations: List[IterationTrace] = field(default_factory=list)

    # 最终结果
    final_success: bool = False
    final_code: str = ""
    total_iterations: int = 0
    termination_reason: str = ""

    # 统计
    error_types_encountered: List[str] = field(default_factory=list)
    tokens_used: int = 0

    def to_dict(self) -> Dict:
        """转换为可序列化的字典"""
        return {
            "task_id": self.task_id,
            "task_prompt": self.task_prompt,
            "duration": (self.end_time - self.start_time).total_seconds(),
            "final_success": self.final_success,
            "total_iterations": self.total_iterations,
            "termination_reason": self.termination_reason,
            "iterations": [
                {
                    "iteration": it.iteration,
                    "code": it.extracted_code,
                    "success": it.execution_success,
                    "error_type": it.structured_error.error_type.value if it.structured_error else None,
                    "reflection": it.reflection.diagnosis if it.reflection else None
                }
                for it in self.iterations
            ]
        }


class ExecutionTracer:
    """执行轨迹记录器"""

    def __init__(self):
        self.current_trace: Optional[TaskTrace] = None

    def start_task(self, task_id: str, prompt: str):
        """开始记录一个任务"""
        self.current_trace = TaskTrace(
            task_id=task_id,
            task_prompt=prompt,
            start_time=datetime.now(),
            end_time=datetime.now()  # 临时值
        )

    def record_iteration(
        self,
        iteration: int,
        llm_output: str,
        code: str,
        execution_result: tuple,
        reflection: Optional[ReflectionEntry],
        decision: str
    ):
        """记录一次迭代"""
        if not self.current_trace:
            return

        trace = IterationTrace(
            iteration=iteration,
            timestamp=datetime.now(),
            input_prompt=self.current_trace.task_prompt,
            context="",  # TODO: 添加上下文
            raw_llm_output=llm_output,
            extracted_code=code,
            execution_success=execution_result[0],
            execution_output=execution_result[1],
            structured_error=execution_result[2] if len(execution_result) > 2 else None,
            reflection=reflection,
            decision=decision,
            decision_reason=""
        )

        self.current_trace.iterations.append(trace)

    def end_task(self, success: bool, final_code: str, reason: str):
        """结束记录"""
        if not self.current_trace:
            return

        self.current_trace.end_time = datetime.now()
        self.current_trace.final_success = success
        self.current_trace.final_code = final_code
        self.current_trace.total_iterations = len(self.current_trace.iterations)
        self.current_trace.termination_reason = reason

        # 统计错误类型
        self.current_trace.error_types_encountered = [
            it.structured_error.error_type.value
            for it in self.current_trace.iterations
            if it.structured_error
        ]

    def save(self, filepath: str):
        """保存轨迹到文件"""
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.current_trace.to_dict(), f, indent=2, ensure_ascii=False)
```

**集成到 Graph：**

```python
# 在 create_graph() 中
tracer = ExecutionTracer()

def coder_node_with_trace(state):
    # 原有逻辑
    result = coder_node(state)

    # 记录轨迹
    tracer.record_iteration(
        iteration=state["iterations"],
        llm_output=result["messages"][-1].content,
        code=result["code"],
        ...
    )

    return result
```

---

### 2. 统计分析引擎

**文件：** `src/evaluation/analyzer.py`

**功能：** 从轨迹中提取洞察

```python
from typing import List, Dict
from collections import Counter
import statistics


class TraceAnalyzer:
    """轨迹分析器"""

    def __init__(self, traces: List[TaskTrace]):
        self.traces = traces

    def compute_summary(self) -> Dict:
        """计算总体统计"""
        return {
            "total_tasks": len(self.traces),
            "success_count": sum(t.final_success for t in self.traces),
            "success_rate": self.success_rate(),
            "avg_iterations": self.avg_iterations(),
            "median_iterations": self.median_iterations(),
            "max_iterations": max(t.total_iterations for t in self.traces),
            "avg_duration": self.avg_duration(),
        }

    def error_distribution(self) -> Dict[str, int]:
        """错误类型分布"""
        all_errors = []
        for trace in self.traces:
            all_errors.extend(trace.error_types_encountered)

        return dict(Counter(all_errors))

    def recovery_rate_by_error(self) -> Dict[str, float]:
        """各类错误的恢复率"""
        error_stats = {}

        for trace in self.traces:
            for error_type in trace.error_types_encountered:
                if error_type not in error_stats:
                    error_stats[error_type] = {"total": 0, "recovered": 0}

                error_stats[error_type]["total"] += 1
                if trace.final_success:
                    error_stats[error_type]["recovered"] += 1

        return {
            etype: stats["recovered"] / stats["total"]
            for etype, stats in error_stats.items()
        }

    def iteration_breakdown(self) -> Dict[int, int]:
        """按迭代次数分组"""
        return dict(Counter(t.total_iterations for t in self.traces))

    def termination_reasons(self) -> Dict[str, int]:
        """终止原因统计"""
        return dict(Counter(t.termination_reason for t in self.traces))

    def success_rate(self) -> float:
        """成功率"""
        if not self.traces:
            return 0.0
        return sum(t.final_success for t in self.traces) / len(self.traces)

    def avg_iterations(self) -> float:
        """平均迭代次数"""
        if not self.traces:
            return 0.0
        return statistics.mean(t.total_iterations for t in self.traces)

    def median_iterations(self) -> float:
        """中位数迭代次数"""
        if not self.traces:
            return 0.0
        return statistics.median(t.total_iterations for t in self.traces)

    def avg_duration(self) -> float:
        """平均执行时长（秒）"""
        if not self.traces:
            return 0.0
        durations = [
            (t.end_time - t.start_time).total_seconds()
            for t in self.traces
        ]
        return statistics.mean(durations)

    def find_interesting_cases(self) -> Dict:
        """找出有意思的案例"""
        return {
            "fastest_success": min(
                (t for t in self.traces if t.final_success),
                key=lambda t: t.total_iterations,
                default=None
            ),
            "most_iterations": max(
                self.traces,
                key=lambda t: t.total_iterations
            ),
            "quick_failures": [
                t for t in self.traces
                if not t.final_success and t.total_iterations == 1
            ],
            "late_successes": [
                t for t in self.traces
                if t.final_success and t.total_iterations >= 4
            ]
        }
```

**使用示例：**

```python
# 加载轨迹
traces = [TaskTrace.from_file(f) for f in trace_files]

# 分析
analyzer = TraceAnalyzer(traces)

summary = analyzer.compute_summary()
print(f"成功率: {summary['success_rate']:.2%}")
print(f"平均迭代: {summary['avg_iterations']:.1f}")

# 错误分布
errors = analyzer.error_distribution()
print("\n错误类型分布:")
for etype, count in errors.items():
    print(f"  {etype}: {count} 次")

# 恢复率
recovery = analyzer.recovery_rate_by_error()
print("\n错误恢复率:")
for etype, rate in recovery.items():
    print(f"  {etype}: {rate:.2%}")
```

---

### 3. 可视化生成器

**文件：** `src/evaluation/visualizer.py`

**功能：** 生成图表

```python
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List


class TraceVisualizer:
    """轨迹可视化器"""

    def __init__(self, analyzer: TraceAnalyzer):
        self.analyzer = analyzer

    def plot_success_rate(self) -> go.Figure:
        """成功率饼图"""
        summary = self.analyzer.compute_summary()

        fig = go.Figure(data=[go.Pie(
            labels=['成功', '失败'],
            values=[
                summary['success_count'],
                summary['total_tasks'] - summary['success_count']
            ],
            marker_colors=['#2ecc71', '#e74c3c']
        )])

        fig.update_layout(title="任务成功率")
        return fig

    def plot_error_distribution(self) -> go.Figure:
        """错误类型分布柱状图"""
        errors = self.analyzer.error_distribution()

        fig = go.Figure(data=[go.Bar(
            x=list(errors.keys()),
            y=list(errors.values()),
            marker_color='#3498db'
        )])

        fig.update_layout(
            title="错误类型分布",
            xaxis_title="错误类型",
            yaxis_title="出现次数"
        )
        return fig

    def plot_recovery_rate(self) -> go.Figure:
        """错误恢复率对比"""
        recovery = self.analyzer.recovery_rate_by_error()

        fig = go.Figure(data=[go.Bar(
            x=list(recovery.keys()),
            y=[r * 100 for r in recovery.values()],
            marker_color='#9b59b6',
            text=[f"{r:.1%}" for r in recovery.values()],
            textposition='auto'
        )])

        fig.update_layout(
            title="各类错误的恢复率",
            xaxis_title="错误类型",
            yaxis_title="恢复率 (%)",
            yaxis_range=[0, 100]
        )
        return fig

    def plot_iteration_distribution(self) -> go.Figure:
        """迭代次数分布"""
        iterations = self.analyzer.iteration_breakdown()

        fig = go.Figure(data=[go.Bar(
            x=list(iterations.keys()),
            y=list(iterations.values()),
            marker_color='#1abc9c'
        )])

        fig.update_layout(
            title="迭代次数分布",
            xaxis_title="迭代次数",
            yaxis_title="任务数量"
        )
        return fig

    def plot_execution_timeline(self, trace: TaskTrace) -> go.Figure:
        """单个任务的执行时间线"""
        iterations = trace.iterations

        # 颜色映射
        colors = []
        for it in iterations:
            if it.execution_success:
                colors.append('green')
            elif it.structured_error:
                colors.append('red')
            else:
                colors.append('orange')

        fig = go.Figure()

        # 添加迭代点
        fig.add_trace(go.Scatter(
            x=[it.iteration for it in iterations],
            y=[1] * len(iterations),
            mode='markers+text',
            marker=dict(size=20, color=colors),
            text=[it.structured_error.error_type.value if it.structured_error else "OK"
                  for it in iterations],
            textposition="top center"
        ))

        fig.update_layout(
            title=f"执行时间线: {trace.task_id}",
            xaxis_title="迭代次数",
            yaxis_visible=False,
            height=300
        )

        return fig

    def save_all_plots(self, output_dir: str):
        """保存所有图表"""
        self.plot_success_rate().write_html(f"{output_dir}/success_rate.html")
        self.plot_error_distribution().write_html(f"{output_dir}/error_dist.html")
        self.plot_recovery_rate().write_html(f"{output_dir}/recovery_rate.html")
        self.plot_iteration_distribution().write_html(f"{output_dir}/iterations.html")
```

---

### 4. HTML 报告生成器

**文件：** `src/reports/generator.py`

**功能：** 生成交互式 HTML 报告

```python
from jinja2 import Template
from pathlib import Path


class ReportGenerator:
    """HTML 报告生成器"""

    def __init__(self, analyzer: TraceAnalyzer, visualizer: TraceVisualizer):
        self.analyzer = analyzer
        self.visualizer = visualizer

    def generate(self, output_path: str):
        """生成完整报告"""
        # 准备数据
        summary = self.analyzer.compute_summary()
        errors = self.analyzer.error_distribution()
        recovery = self.analyzer.recovery_rate_by_error()
        cases = self.analyzer.find_interesting_cases()

        # 生成图表
        plots = {
            "success_rate": self.visualizer.plot_success_rate().to_html(full_html=False),
            "error_dist": self.visualizer.plot_error_distribution().to_html(full_html=False),
            "recovery": self.visualizer.plot_recovery_rate().to_html(full_html=False),
            "iterations": self.visualizer.plot_iteration_distribution().to_html(full_html=False)
        }

        # 渲染模板
        template = self.load_template()
        html = template.render(
            summary=summary,
            errors=errors,
            recovery=recovery,
            cases=cases,
            plots=plots
        )

        # 保存
        Path(output_path).write_text(html, encoding='utf-8')

    def load_template(self) -> Template:
        """加载 HTML 模板"""
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>Coding Agent 评测报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .summary { background: #f0f0f0; padding: 20px; border-radius: 10px; }
        .metric { display: inline-block; margin: 10px 20px; }
        .chart { margin: 30px 0; }
        .case { border-left: 4px solid #3498db; padding-left: 20px; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>🤖 Coding Agent 执行报告</h1>

    <div class="summary">
        <h2>📊 总体统计</h2>
        <div class="metric">
            <strong>总任务数:</strong> {{ summary.total_tasks }}
        </div>
        <div class="metric">
            <strong>成功率:</strong> {{ "%.2f%%" | format(summary.success_rate * 100) }}
        </div>
        <div class="metric">
            <strong>平均迭代:</strong> {{ "%.1f" | format(summary.avg_iterations) }}
        </div>
        <div class="metric">
            <strong>平均耗时:</strong> {{ "%.1f秒" | format(summary.avg_duration) }}
        </div>
    </div>

    <div class="chart">
        <h2>📈 成功率分布</h2>
        {{ plots.success_rate | safe }}
    </div>

    <div class="chart">
        <h2>🐛 错误类型分布</h2>
        {{ plots.error_dist | safe }}
    </div>

    <div class="chart">
        <h2>🔄 错误恢复率</h2>
        {{ plots.recovery | safe }}
    </div>

    <div class="chart">
        <h2>🔁 迭代次数分布</h2>
        {{ plots.iterations | safe }}
    </div>

    <h2>💡 典型案例</h2>

    {% if cases.fastest_success %}
    <div class="case">
        <h3>⚡ 最快成功案例</h3>
        <p>任务: {{ cases.fastest_success.task_prompt[:100] }}...</p>
        <p>迭代: {{ cases.fastest_success.total_iterations }} 次</p>
    </div>
    {% endif %}

    {% if cases.late_successes %}
    <div class="case">
        <h3>🎯 迟来的成功（≥4次迭代）</h3>
        <ul>
        {% for case in cases.late_successes[:3] %}
            <li>{{ case.task_id }}: {{ case.total_iterations }} 次迭代</li>
        {% endfor %}
        </ul>
    </div>
    {% endif %}

</body>
</html>
        """
        return Template(template_str)
```

**使用示例：**

```python
# 运行评测
traces = run_evaluation()

# 分析
analyzer = TraceAnalyzer(traces)
visualizer = TraceVisualizer(analyzer)

# 生成报告
generator = ReportGenerator(analyzer, visualizer)
generator.generate("reports/evaluation_report.html")

print("报告已生成: reports/evaluation_report.html")
# 在浏览器中打开即可查看交互式报告
```

---

### 5. 对比实验框架

**文件：** `src/experiments/ablation.py`

**功能：** A/B 测试

```python
class AblationExperiment:
    """消融实验"""

    def run_with_reflection(self, tasks):
        """带反思的版本"""
        graph = create_graph(enable_reflection=True)
        return run_tasks(graph, tasks)

    def run_without_reflection(self, tasks):
        """不带反思的版本"""
        graph = create_graph(enable_reflection=False)
        return run_tasks(graph, tasks)

    def compare(self, tasks):
        """对比实验"""
        print("运行带反思版本...")
        with_ref = self.run_with_reflection(tasks)

        print("运行无反思版本...")
        without_ref = self.run_without_reflection(tasks)

        # 分析差异
        return {
            "with_reflection": {
                "success_rate": analyze(with_ref).success_rate(),
                "avg_iterations": analyze(with_ref).avg_iterations()
            },
            "without_reflection": {
                "success_rate": analyze(without_ref).success_rate(),
                "avg_iterations": analyze(without_ref).avg_iterations()
            },
            "lift": {
                "success_rate": ...,
                "iterations": ...
            }
        }
```

**报告输出：**

```
对比实验结果:

有反思机制:
  成功率: 52%
  平均迭代: 2.3 次

无反思机制:
  成功率: 35%
  平均迭代: 1.8 次

提升:
  成功率: +17% ← 核心发现！
  平均成本: +0.5 次迭代

结论: 反思机制以 28% 的成本增加换来了 49% 的成功率提升
```

---

## 📈 预期产出

完成阶段 2 后，你将获得：

### 1. 交互式 HTML 报告

```
reports/
├── evaluation_report.html  ← 主报告
├── plots/
│   ├── success_rate.png
│   ├── error_distribution.png
│   └── recovery_rate.png
└── traces/
    ├── task_001.json
    └── task_002.json
```

### 2. 数据分析结果

```python
{
    "total_tasks": 50,
    "success_rate": 0.52,
    "pass@1": 0.35,
    "correction_lift": 0.17,  # +17%
    "error_recovery": {
        "syntax": 0.85,
        "import": 0.78,
        "runtime": 0.45,
        "logic": 0.12
    }
}
```

### 3. 可视化图表

- 📊 成功率饼图
- 📈 错误类型分布
- 🔄 错误恢复率对比
- 🔁 迭代次数分布
- ⏱️ 执行时间线

### 4. 典型案例分析

```
案例 1: 快速成功
任务: "写一个排序函数"
迭代 1: SyntaxError（缺少冒号）
迭代 2: ✅ 成功
反思: "函数定义需要冒号"

案例 2: 逻辑错误难恢复
任务: "实现二分查找"
迭代 1-5: 逻辑错误（边界条件）
结果: ❌ 失败
结论: 逻辑推理超出模型能力
```

---

## 🛠️ 实施计划

### 第 1 步：轨迹记录（3-4 小时）

- [ ] 实现 `ExecutionTracer`
- [ ] 集成到 Graph
- [ ] 测试记录完整性

### 第 2 步：统计分析（2-3 小时）

- [ ] 实现 `TraceAnalyzer`
- [ ] 编写分析函数
- [ ] 单元测试

### 第 3 步：可视化（3-4 小时）

- [ ] 安装 plotly
- [ ] 实现各类图表
- [ ] 调整样式

### 第 4 步：报告生成（2-3 小时）

- [ ] 编写 HTML 模板
- [ ] 实现 `ReportGenerator`
- [ ] 测试报告生成

### 第 5 步：对比实验（2 小时）

- [ ] 实现消融实验
- [ ] 运行对比
- [ ] 分析差异

**总计：** 约 12-16 小时（2-3 天）

---

## 🎓 论文/报告可用内容

完成后可以写：

### 图表

> 图 1: 错误类型分布
> 图 2: 各类错误的恢复率
> 图 3: 迭代次数分布
> 图 4: 消融实验对比

### 案例研究

> 4.1 成功案例分析
> 通过执行轨迹可见，系统在第2次迭代成功修复了导入错误...

> 4.2 失败案例分析
> 逻辑错误在5次迭代中均未恢复，反思记录显示模型反复输出相似策略...

### 消融研究

> 表 1: 消融实验结果
> 反思机制贡献了 17% 的成功率提升，证明了其有效性。

---

## 📊 成功标准

完成阶段 2 后，你应该能够：

1. ✅ 打开 HTML 报告展示完整结果
2. ✅ 导出高质量图表用于论文/PPT
3. ✅ 回放任何任务的执行过程
4. ✅ 对比有无反思的差异
5. ✅ 找出系统的优势和弱点

---

这就是**阶段 2 的完整方案**。
