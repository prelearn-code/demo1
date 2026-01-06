#!/usr/bin/env python3
"""
Coding Agent - 带状态可视化的演示版本
实时显示 Graph 执行过程和状态变化
"""
from langchain_core.messages import HumanMessage
from src.agent import create_graph
from src.config import settings
import json


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔═══════════════════════════════════════════════════╗
║   🤖 Coding Agent - 状态可视化版本                ║
║   实时显示 Graph 执行流程                         ║
╚═══════════════════════════════════════════════════╝
"""
    print(banner)
    print(f"模型: {settings.ollama_model}")
    print(f"最大迭代: {settings.max_iterations}")
    print("-" * 55)


def print_state_summary(state: dict, node_name: str = None):
    """
    打印状态摘要

    Args:
        state: 当前状态
        node_name: 当前节点名称
    """
    if node_name:
        print(f"\n{'='*55}")
        print(f"📍 当前节点: {node_name.upper()}")
        print(f"{'='*55}")

    print(f"\n📊 状态快照:")
    print(f"  - 迭代次数: {state.get('iterations', 0)}/{settings.max_iterations}")
    print(f"  - 代码状态: {'✅ 已生成' if state.get('code') else '⚪ 未生成'}")
    print(f"  - 执行结果: {'✅ 成功' if state.get('execution_result') else '⚪ 未执行'}")
    print(f"  - 错误信息: {'❌ 有错误' if state.get('error') else '✅ 无错误'}")

    if state.get('code'):
        code_preview = state['code'][:100].replace('\n', ' ')
        print(f"  - 代码预览: {code_preview}...")

    if state.get('error'):
        error_preview = state['error'][:80].replace('\n', ' ')
        print(f"  - 错误预览: {error_preview}...")


def visualize_graph_flow(current_node: str, iteration: int):
    """
    可视化当前 Graph 流程位置

    Args:
        current_node: 当前节点
        iteration: 当前迭代次数
    """
    nodes = {
        "__start__": "🚀 START",
        "coder": "💻 CODER",
        "executor": "⚙️  EXECUTOR",
        "reflector": "🔍 REFLECTOR",
        "__end__": "🏁 END"
    }

    flow = ["__start__", "coder", "executor", "reflector"]

    print(f"\n🗺️  执行流程 (第 {iteration} 轮):")
    print("┌" + "─" * 53 + "┐")

    for node in flow:
        if node == current_node:
            print(f"│ ➤ {nodes.get(node, node):50} │ ← 当前")
        else:
            print(f"│   {nodes.get(node, node):50} │")

    print("└" + "─" * 53 + "┘")


def main_with_stream():
    """使用 stream 模式的主函数"""
    print_banner()

    # 示例任务
    examples = [
        "写一个函数计算斐波那契数列的第10项",
        "生成1-100之间的所有质数",
        "实现一个简单的加法计算器"
    ]

    print("\n示例任务:")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")

    print("\n请输入你的编程任务 (或输入数字选择示例):")
    user_input = input("> ").strip()

    # 处理输入
    if user_input.isdigit() and 1 <= int(user_input) <= len(examples):
        task = examples[int(user_input) - 1]
    else:
        task = user_input

    if not task:
        print("❌ 任务不能为空")
        return

    print(f"\n📝 任务: {task}")
    print("=" * 55)

    # 创建图
    graph = create_graph()

    # 初始化状态
    initial_state = {
        "messages": [HumanMessage(content=task)],
        "code": None,
        "execution_result": None,
        "error": None,
        "iterations": 0
    }

    print("\n🎬 开始执行 Graph 流程...")
    print("=" * 55)

    # 使用 stream 模式执行
    try:
        final_state = None

        # stream() 会返回每个节点执行后的状态
        for step_output in graph.stream(initial_state):
            # step_output 格式: {node_name: state}
            for node_name, state in step_output.items():
                # 可视化流程
                visualize_graph_flow(node_name, state.get("iterations", 0))

                # 打印状态摘要
                print_state_summary(state, node_name)

                # 保存最终状态
                final_state = state

                # 添加分隔符
                print("\n" + "─" * 55)
                input("按 Enter 继续下一步...")

        # 打印最终结果
        print("\n" + "=" * 55)
        print("🏁 执行完成!")
        print("=" * 55)

        if final_state:
            print("\n📊 最终结果:")

            if final_state.get("execution_result"):
                print("\n✅ 任务成功完成!")
                print(f"\n📄 最终代码:")
                print(f"```python\n{final_state['code']}\n```")
                print(f"\n📤 执行输出:")
                print(final_state['execution_result'])
            else:
                print("\n❌ 任务失败!")
                if final_state.get("error"):
                    print(f"\n⚠️  最后错误:")
                    print(final_state['error'])
                if final_state.get('code'):
                    print(f"\n📄 最后生成的代码:")
                    print(f"```python\n{final_state['code']}\n```")

            print(f"\n📈 统计信息:")
            print(f"  - 总迭代次数: {final_state.get('iterations', 0)}")
            print(f"  - 消息数量: {len(final_state.get('messages', []))}")

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
    except Exception as e:
        print(f"\n\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()


def main_with_invoke():
    """使用 invoke 模式的主函数（快速执行，无暂停）"""
    print_banner()

    # 示例任务
    examples = [
        "写一个函数计算斐波那契数列的第10项",
        "生成1-100之间的所有质数",
        "实现一个简单的加法计算器"
    ]

    print("\n示例任务:")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")

    print("\n请输入你的编程任务 (或输入数字选择示例):")
    user_input = input("> ").strip()

    # 处理输入
    if user_input.isdigit() and 1 <= int(user_input) <= len(examples):
        task = examples[int(user_input) - 1]
    else:
        task = user_input

    if not task:
        print("❌ 任务不能为空")
        return

    print(f"\n📝 任务: {task}")
    print("=" * 55)

    # 创建图
    graph = create_graph()

    # 初始化状态
    initial_state = {
        "messages": [HumanMessage(content=task)],
        "code": None,
        "execution_result": None,
        "error": None,
        "iterations": 0
    }

    print("\n🎬 开始执行 Graph 流程 (自动模式)...")
    print("=" * 55)

    try:
        # 使用 stream 但不暂停
        final_state = None

        for step_output in graph.stream(initial_state):
            for node_name, state in step_output.items():
                # 简化的状态显示
                print(f"\n▶️  执行节点: {node_name}")
                print(f"   迭代: {state.get('iterations', 0)}, "
                      f"状态: {'✅ 成功' if state.get('execution_result') else '🔄 进行中'}")

                final_state = state

        # 打印最终结果
        print("\n" + "=" * 55)
        print("🏁 执行完成!")
        print("=" * 55)

        if final_state:
            if final_state.get("execution_result"):
                print("\n✅ 成功!")
                print(f"\n最终代码:\n```python\n{final_state['code']}\n```")
                print(f"\n执行输出:\n{final_state['execution_result']}")
            else:
                print("\n❌ 失败!")
                if final_state.get("error"):
                    print(f"\n最后错误:\n{final_state['error']}")
                print(f"\n最后生成的代码:\n```python\n{final_state.get('code', '无')}\n```")

            print(f"\n总迭代次数: {final_state['iterations']}")

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n选择执行模式:")
    print("  1. 🐢 逐步模式 (每步暂停，显示详细状态)")
    print("  2. 🚀 自动模式 (连续执行，显示简要状态)")

    mode = input("\n请选择 (1/2，默认2): ").strip()

    if mode == "1":
        main_with_stream()
    else:
        main_with_invoke()
