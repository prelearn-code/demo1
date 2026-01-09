#!/usr/bin/env python3
"""
Coding Agent Local - 主入口
本地 Ollama 编程助手演示
"""
from langchain_core.messages import HumanMessage
from src.agent import create_graph
from src.config import settings


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔═══════════════════════════════════════════════════╗
║      🤖 Coding Agent Local - Ollama Demo         ║
║      基于 LangGraph + Qwen2.5-Coder-7B            ║
╚═══════════════════════════════════════════════════╝
"""
    print(banner)
    print(f"模型: {settings.ollama_model}")
    print(f"最大迭代: {settings.max_iterations}")
    print(f"温度: {settings.temperature}")
    print("-" * 55)


def main():
    """主函数"""
    print_banner()

    # 示例任务
    examples = [
        "写一个函数计算斐波那契数列的第n项",
        "生成1-100之间的所有质数",
        "实现一个简单的计算器(支持加减乘除)"
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
        "iterations": 0,
        # 阶段三新增字段
        "structured_error": None,
        "route_result": None,
        "test_input": None,
        "reflection_history": [],
        "matched_rule_id": None
    }

    # 执行图
    try:
        final_state = graph.invoke(initial_state)

        # 打印最终结果
        print("\n" + "=" * 55)
        print("📊 最终结果:")
        print("=" * 55)

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
    main()
