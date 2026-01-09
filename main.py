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
║      🤖 Coding Agent - 智能代码生成助手           ║
║      支持 Python/JS/Java/C++/Go/Rust 等 8 种语言  ║
╚═══════════════════════════════════════════════════╝
"""
    print(banner)
    print(f"模型: {settings.ollama_model}")
    print(f"最大迭代: {settings.max_iterations}")
    print(f"温度: {settings.temperature}")
    print(f"🌍 多语言: 自动检测并执行")
    print("-" * 55)


def main():
    """主函数"""
    print_banner()

    # 示例任务（支持多语言）
    examples = [
        "用 Python 写一个函数计算斐波那契数列的第n项",
        "用 JavaScript 实现数组去重功能",
        "用 C++ 实现快速排序算法",
        "用 Go 写一个并发的 Hello World",
        "生成1-100之间的所有质数（任意语言）"
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
        "matched_rule_id": None,
        # 多语言支持字段
        "language_hint": None,
        "detected_language": None
    }

    # 执行图
    try:
        final_state = graph.invoke(initial_state)

        # 打印最终结果
        print("\n" + "=" * 55)
        print("📊 最终结果:")
        print("=" * 55)

        # 获取检测到的语言
        detected_lang = final_state.get("detected_language", "python")

        if final_state.get("execution_result"):
            print("\n✅ 成功!")
            print(f"\n执行语言: {detected_lang}")
            print(f"\n最终代码:\n```{detected_lang}\n{final_state['code']}\n```")
            print(f"\n执行输出:\n{final_state['execution_result']}")
        else:
            print("\n❌ 失败!")
            if final_state.get("error"):
                print(f"\n最后错误:\n{final_state['error']}")
            if final_state.get("detected_language"):
                print(f"\n尝试执行语言: {detected_lang}")
            print(f"\n最后生成的代码:\n```{detected_lang}\n{final_state.get('code', '无')}\n```")

        print(f"\n总迭代次数: {final_state['iterations']}")

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
