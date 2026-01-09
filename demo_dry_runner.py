#!/usr/bin/env python3
"""
DryRunner 执行追踪演示
展示如何使用轻量级执行追踪来调试代码逻辑错误
"""

from src.debugging import DryRunner, format_trace


def demo_fibonacci():
    """演示斐波那契追踪"""
    print("=" * 60)
    print("演示 1: 斐波那契数列执行追踪")
    print("=" * 60)

    code = """
def fibonacci(n):
    a, b = 0, 1
    for i in range(n):
        a, b = b, a + b
    return a

result = fibonacci(5)
"""

    runner = DryRunner()
    trace = runner.trace_execution(code, {"n": 5})

    print(f"\n代码:\n{code}")
    print(f"\n执行追踪:")
    print(format_trace(trace))

    print(f"\n分析:")
    print("可以看到 a 和 b 的值在每次迭代中如何变化")


def demo_division_by_zero():
    """演示除零错误检测"""
    print("\n" + "=" * 60)
    print("演示 2: 除零错误检测")
    print("=" * 60)

    code = """
def safe_divide(x, y):
    result = x / y
    return result

z = safe_divide(10, 0)
"""

    runner = DryRunner()
    trace = runner.trace_execution(code, {"x": 10, "y": 0})

    print(f"\n代码:\n{code}")
    print(f"\n执行追踪:")
    print(format_trace(trace))

    # 检查是否有除零
    for step in trace:
        if step.get("value") == "DIVISION_BY_ZERO":
            print(f"\n⚠️  检测到除零错误在第 {step['line']} 行!")


def demo_logic_error():
    """演示逻辑错误检测"""
    print("\n" + "=" * 60)
    print("演示 3: 逻辑错误检测")
    print("=" * 60)

    # 这个代码有逻辑错误：应该返回最大值，但返回了最小值
    code = """
def find_max(a, b):
    if a > b:
        result = b
    else:
        result = a
    return result

max_value = find_max(10, 5)
"""

    runner = DryRunner()
    trace = runner.trace_execution(code, {"a": 10, "b": 5})

    print(f"\n代码:\n{code}")
    print(f"\n执行追踪:")
    print(format_trace(trace))

    print(f"\n分析:")
    print("追踪显示当 a > b (10 > 5) 时，返回了 b (5)")
    print("这与函数名 'find_max' 的预期不符 - 这是一个逻辑错误!")


def demo_loop_analysis():
    """演示循环分析"""
    print("\n" + "=" * 60)
    print("演示 4: 循环次数分析")
    print("=" * 60)

    code = """
def sum_range(n):
    total = 0
    for i in range(n):
        total += i
    return total

result = sum_range(5)
"""

    runner = DryRunner()
    trace = runner.trace_execution(code, {"n": 5})

    print(f"\n代码:\n{code}")
    print(f"\n执行追踪:")
    print(format_trace(trace))

    # 统计循环次数
    loop_count = sum(1 for step in trace if step.get("type") == "augassign")
    print(f"\n分析:")
    print(f"循环执行了 {loop_count} 次")
    print(f"total 的最终值: {[s['new_value'] for s in trace if s.get('type') == 'augassign'][-1] if loop_count > 0 else 0}")


def demo_conditional_branches():
    """演示条件分支追踪"""
    print("\n" + "=" * 60)
    print("演示 5: 条件分支追踪")
    print("=" * 60)

    code = """
def classify_number(x):
    if x > 0:
        category = "positive"
    elif x < 0:
        category = "negative"
    else:
        category = "zero"
    return category

result = classify_number(-5)
"""

    runner = DryRunner()
    trace = runner.trace_execution(code, {"x": -5})

    print(f"\n代码:\n{code}")
    print(f"\n执行追踪:")
    print(format_trace(trace))

    print(f"\n分析:")
    conditions = [s for s in trace if s.get("type") == "condition"]
    if conditions:
        for cond in conditions:
            print(f"条件 '{cond.get('condition', '???')}' 结果: {cond.get('result')}")


def demo_complex_expressions():
    """演示复杂表达式计算"""
    print("\n" + "=" * 60)
    print("演示 6: 复杂表达式追踪")
    print("=" * 60)

    code = """
def calculate(a, b, c):
    x = a + b
    y = x * c
    z = y - a
    result = z / b
    return result

final = calculate(10, 5, 3)
"""

    runner = DryRunner()
    trace = runner.trace_execution(code, {"a": 10, "b": 5, "c": 3})

    print(f"\n代码:\n{code}")
    print(f"\n执行追踪:")
    print(format_trace(trace))

    print(f"\n分析:")
    print("可以清楚地看到每个中间变量的值:")
    assigns = [s for s in trace if s.get("type") == "assign"]
    for assign in assigns:
        print(f"  {assign['var']} = {assign['value']}")


def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════╗
║      🔍 DryRunner 执行追踪演示                    ║
║      轻量级代码执行分析                            ║
╚═══════════════════════════════════════════════════╝
""")

    demos = [
        demo_fibonacci,
        demo_division_by_zero,
        demo_logic_error,
        demo_loop_analysis,
        demo_conditional_branches,
        demo_complex_expressions
    ]

    print("\n运行所有演示...\n")

    for demo in demos:
        demo()
        input("\n按 Enter 继续...")

    print("\n" + "=" * 60)
    print("✅ 所有演示完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
