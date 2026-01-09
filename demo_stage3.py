#!/usr/bin/env python3
"""
阶段三功能演示脚本
展示规则库、执行追踪、错误路由和多模型管理功能
"""

from langchain_core.messages import HumanMessage
from src.agent import create_graph
from src.agent.nodes import _rule_base, _error_router
from src.learning import RuleBase
from src.debugging import DryRunner, format_trace
from src.agent.errors import ErrorParser, ErrorType
from src.models import ModelManager


def print_banner():
    """打印横幅"""
    banner = """
╔═══════════════════════════════════════════════════╗
║      🚀 阶段三高级特性演示                         ║
║      规则库 | 执行追踪 | 错误路由 | 多模型          ║
╚═══════════════════════════════════════════════════╝
"""
    print(banner)


def demo_rule_base():
    """演示规则库功能"""
    print("\n" + "=" * 60)
    print("📚 演示 1: 规则库 (RuleBase)")
    print("=" * 60)

    # 获取规则统计
    stats = _rule_base.get_statistics()
    print(f"\n规则库统计:")
    print(f"  总规则数: {stats['total_rules']}")
    print(f"  已使用规则数: {stats['used_rules']}")
    print(f"  总应用次数: {stats['total_applications']}")
    print(f"  总成功次数: {stats['total_successes']}")

    # 显示内置规则
    print(f"\n内置规则示例 (前5个):")
    for i, rule in enumerate(_rule_base.rules[:5], 1):
        print(f"\n  {i}. {rule.rule_id}")
        print(f"     错误类型: {rule.error_type.value}")
        print(f"     置信度: {rule.confidence:.2f}")
        print(f"     诊断: {rule.diagnosis}")
        print(f"     修复建议: {rule.fix_template}")

    # 演示错误匹配
    print("\n" + "-" * 60)
    print("演示错误匹配:")

    test_errors = [
        ("name 'math' is not defined", ErrorType.IMPORT),
        ("SyntaxError: invalid syntax", ErrorType.SYNTAX),
        ("ZeroDivisionError: division by zero", ErrorType.RUNTIME),
    ]

    for error_msg, error_type in test_errors:
        stderr = f"{error_msg}"
        code = "x = 10 / 0"
        structured_error = ErrorParser.parse(stderr, code)

        print(f"\n错误: {error_msg}")
        matched_rules = _rule_base.match(structured_error)

        if matched_rules:
            best_rule = matched_rules[0]
            print(f"  ✓ 匹配到规则: {best_rule.rule_id}")
            print(f"  置信度: {best_rule.confidence:.2f}")
            print(f"  建议: {best_rule.fix_template}")
        else:
            print(f"  ✗ 未匹配到规则")


def demo_dry_runner():
    """演示执行追踪功能"""
    print("\n" + "=" * 60)
    print("🔍 演示 2: 轻量级执行追踪 (DryRunner)")
    print("=" * 60)

    runner = DryRunner()

    # 示例代码
    test_cases = [
        {
            "name": "简单斐波那契",
            "code": """
def fibonacci(n):
    a, b = 0, 1
    for i in range(n):
        a, b = b, a + b
    return a
""",
            "input": {"n": 5}
        },
        {
            "name": "除法计算",
            "code": """
def divide(x, y):
    result = x / y
    return result
""",
            "input": {"x": 10, "y": 0}
        }
    ]

    for case in test_cases:
        print(f"\n测试: {case['name']}")
        print(f"代码:\n{case['code']}")
        print(f"输入: {case['input']}")

        trace = runner.trace_execution(case['code'], case['input'])
        trace_str = format_trace(trace)

        print(f"\n执行追踪:")
        print(trace_str)


def demo_error_router():
    """演示错误路由功能"""
    print("\n" + "=" * 60)
    print("🔀 演示 3: 错误路由器 (ErrorRouter)")
    print("=" * 60)

    # 模拟不同类型的错误
    error_cases = [
        {
            "type": "语法错误",
            "stderr": "SyntaxError: invalid syntax",
            "code": "def foo()\n    pass"
        },
        {
            "type": "导入错误",
            "stderr": "NameError: name 'math' is not defined",
            "code": "x = math.sqrt(16)"
        },
        {
            "type": "运行时错误",
            "stderr": "ZeroDivisionError: division by zero",
            "code": "x = 10 / 0"
        },
        {
            "type": "超时错误",
            "stderr": "TimeoutError: execution timed out",
            "code": "while True: pass"
        }
    ]

    for case in error_cases:
        print(f"\n测试: {case['type']}")
        print(f"错误信息: {case['stderr']}")

        # 解析错误
        structured_error = ErrorParser.parse(case['stderr'], case['code'])

        # 创建模拟状态
        state = {
            "code": case['code'],
            "error": case['stderr'],
            "structured_error": structured_error,
            "test_input": {}
        }

        # 路由错误
        route_result = _error_router.route(state)

        print(f"  策略: {route_result['strategy']}")
        print(f"  错误类型: {route_result['error_type']}")
        if 'suggestion' in route_result:
            print(f"  建议: {route_result['suggestion'][:100]}...")
        if 'matched_rule' in route_result:
            print(f"  匹配规则: {route_result['matched_rule']}")


def demo_model_manager():
    """演示多模型管理功能"""
    print("\n" + "=" * 60)
    print("🤖 演示 4: 多模型管理器 (ModelManager)")
    print("=" * 60)

    manager = ModelManager()

    # 列出所有可用模型
    print("\n可用模型:")
    models = manager.list_models()
    for i, model in enumerate(models, 1):
        print(f"\n  {i}. {model['name']}")
        print(f"     模型ID: {model['model_id']}")
        print(f"     描述: {model['description']}")

    # 模拟对比结果
    print("\n" + "-" * 60)
    print("模拟对比实验结果:")

    mock_results = {
        "qwen-7b": {
            "success_rate": 0.52,
            "avg_iterations": 2.3,
            "correction_lift": 0.17,
            "total_tasks": 20,
            "avg_time": 15.2
        },
        "qwen-14b": {
            "success_rate": 0.61,
            "avg_iterations": 2.1,
            "correction_lift": 0.19,
            "total_tasks": 20,
            "avg_time": 23.8
        },
        "deepseek": {
            "success_rate": 0.48,
            "avg_iterations": 2.5,
            "correction_lift": 0.15,
            "total_tasks": 20,
            "avg_time": 18.5
        }
    }

    report = manager.compare_report(mock_results)
    print(f"\n{report}")


def demo_integration():
    """演示集成使用"""
    print("\n" + "=" * 60)
    print("🔧 演示 5: 集成使用 - 运行一个简单任务")
    print("=" * 60)

    task = "写一个函数计算两个数的最大公约数"

    print(f"\n任务: {task}")
    print("开始执行...")

    # 创建图
    graph = create_graph()

    # 初始化状态
    initial_state = {
        "messages": [HumanMessage(content=task)],
        "code": None,
        "execution_result": None,
        "error": None,
        "iterations": 0,
        "structured_error": None,
        "route_result": None,
        "test_input": None,
        "reflection_history": [],
        "matched_rule_id": None
    }

    try:
        final_state = graph.invoke(initial_state)

        print("\n执行完成!")
        print(f"迭代次数: {final_state['iterations']}")

        if final_state.get("execution_result"):
            print("✅ 成功!")
            print(f"\n最终代码:\n```python\n{final_state['code']}\n```")
        else:
            print("❌ 失败")
            if final_state.get("error"):
                print(f"错误: {final_state['error'][:200]}")

        # 显示规则库统计
        if final_state.get("matched_rule_id"):
            print(f"\n使用的规则: {final_state['matched_rule_id']}")

        # 显示反思历史
        if final_state.get("reflection_history"):
            print(f"\n反思历史: {len(final_state['reflection_history'])} 条记录")

    except Exception as e:
        print(f"\n执行出错: {e}")


def main():
    """主函数"""
    print_banner()

    demos = [
        ("规则库", demo_rule_base),
        ("执行追踪", demo_dry_runner),
        ("错误路由", demo_error_router),
        ("多模型管理", demo_model_manager),
        ("集成使用", demo_integration),
        ("运行所有演示", None)
    ]

    print("\n请选择要运行的演示:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")

    choice = input("\n> ").strip()

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(demos) - 1:
            # 运行单个演示
            _, demo_func = demos[idx]
            demo_func()
        elif idx == len(demos) - 1:
            # 运行所有演示
            for name, demo_func in demos[:-1]:
                demo_func()
                input("\n按 Enter 继续下一个演示...")
        else:
            print("无效选择")
    except (ValueError, IndexError):
        print("无效选择")


if __name__ == "__main__":
    main()
