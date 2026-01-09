#!/usr/bin/env python3
"""
多语言代码执行演示
展示如何执行 Python, JavaScript, C++, Go, Rust 等语言
"""

from src.tools.multi_language_sandbox import (
    execute_code_multi_language,
    Language,
    get_supported_languages
)


def print_banner():
    """打印横幅"""
    banner = """
╔═══════════════════════════════════════════════════╗
║      🌍 多语言代码执行演示                         ║
║      支持 Python, JS, Java, C++, Go, Rust 等       ║
╚═══════════════════════════════════════════════════╝
"""
    print(banner)


def demo_python():
    """演示 Python"""
    print("\n" + "=" * 60)
    print("🐍 演示 1: Python")
    print("=" * 60)

    code = """
def fibonacci(n):
    a, b = 0, 1
    for i in range(n):
        a, b = b, a + b
    return a

for i in range(10):
    print(f"fibonacci({i}) = {fibonacci(i)}")
"""

    print(f"代码:\n{code}")
    success, output, lang = execute_code_multi_language(code, Language.PYTHON)

    print(f"\n语言: {lang.value}")
    print(f"状态: {'✓ 成功' if success else '✗ 失败'}")
    print(f"输出:\n{output}")


def demo_javascript():
    """演示 JavaScript"""
    print("\n" + "=" * 60)
    print("📜 演示 2: JavaScript")
    print("=" * 60)

    code = """
function fibonacci(n) {
    let a = 0, b = 1;
    for (let i = 0; i < n; i++) {
        [a, b] = [b, a + b];
    }
    return a;
}

for (let i = 0; i < 10; i++) {
    console.log(`fibonacci(${i}) = ${fibonacci(i)}`);
}
"""

    print(f"代码:\n{code}")
    success, output, lang = execute_code_multi_language(code, Language.JAVASCRIPT)

    print(f"\n语言: {lang.value}")
    print(f"状态: {'✓ 成功' if success else '✗ 失败'}")
    print(f"输出:\n{output}")


def demo_cpp():
    """演示 C++"""
    print("\n" + "=" * 60)
    print("⚙️  演示 3: C++")
    print("=" * 60)

    code = """
#include <iostream>
#include <vector>
using namespace std;

int fibonacci(int n) {
    int a = 0, b = 1;
    for (int i = 0; i < n; i++) {
        int temp = a;
        a = b;
        b = temp + b;
    }
    return a;
}

int main() {
    for (int i = 0; i < 10; i++) {
        cout << "fibonacci(" << i << ") = " << fibonacci(i) << endl;
    }
    return 0;
}
"""

    print(f"代码:\n{code}")
    success, output, lang = execute_code_multi_language(code, Language.CPP)

    print(f"\n语言: {lang.value}")
    print(f"状态: {'✓ 成功' if success else '✗ 失败'}")
    print(f"输出:\n{output}")


def demo_go():
    """演示 Go"""
    print("\n" + "=" * 60)
    print("🐹 演示 4: Go")
    print("=" * 60)

    code = """
package main

import "fmt"

func fibonacci(n int) int {
    a, b := 0, 1
    for i := 0; i < n; i++ {
        a, b = b, a+b
    }
    return a
}

func main() {
    for i := 0; i < 10; i++ {
        fmt.Printf("fibonacci(%d) = %d\\n", i, fibonacci(i))
    }
}
"""

    print(f"代码:\n{code}")
    success, output, lang = execute_code_multi_language(code, Language.GO)

    print(f"\n语言: {lang.value}")
    print(f"状态: {'✓ 成功' if success else '✗ 失败'}")
    print(f"输出:\n{output}")


def demo_auto_detect():
    """演示自动检测"""
    print("\n" + "=" * 60)
    print("🔍 演示 5: 自动语言检测")
    print("=" * 60)

    test_codes = [
        ("Python", "print('Hello from Python!')"),
        ("JavaScript", "console.log('Hello from JavaScript!');"),
        ("C", "#include <stdio.h>\nint main() { printf(\"Hello from C!\\\\n\"); return 0; }"),
    ]

    for name, code in test_codes:
        print(f"\n测试代码 ({name}):")
        print(f"{code[:50]}...")

        success, output, detected_lang = execute_code_multi_language(code)

        print(f"检测到的语言: {detected_lang.value}")
        print(f"状态: {'✓ 成功' if success else '✗ 失败'}")
        print(f"输出: {output[:100]}...")


def demo_comparison():
    """演示不同语言实现相同功能"""
    print("\n" + "=" * 60)
    print("📊 演示 6: 多语言对比 - 计算 1-100 的和")
    print("=" * 60)

    implementations = {
        "Python": """
total = sum(range(1, 101))
print(f"Sum: {total}")
""",
        "JavaScript": """
let total = 0;
for (let i = 1; i <= 100; i++) {
    total += i;
}
console.log(`Sum: ${total}`);
""",
        "C++": """
#include <iostream>
using namespace std;

int main() {
    int total = 0;
    for (int i = 1; i <= 100; i++) {
        total += i;
    }
    cout << "Sum: " << total << endl;
    return 0;
}
""",
        "Go": """
package main
import "fmt"

func main() {
    total := 0
    for i := 1; i <= 100; i++ {
        total += i
    }
    fmt.Printf("Sum: %d\\n", total)
}
"""
    }

    for lang_name, code in implementations.items():
        print(f"\n{lang_name}:")
        success, output, _ = execute_code_multi_language(code)
        if success:
            print(f"✓ {output.strip()}")
        else:
            print(f"✗ 失败: {output[:50]}...")


def demo_error_handling():
    """演示错误处理"""
    print("\n" + "=" * 60)
    print("⚠️  演示 7: 错误处理")
    print("=" * 60)

    # 语法错误
    print("\n测试 1: Python 语法错误")
    code = "print('Hello'"  # 缺少右括号
    success, output, _ = execute_code_multi_language(code, Language.PYTHON)
    print(f"状态: {'✓ 成功' if success else '✗ 失败'}")
    print(f"错误信息:\n{output}")

    # 运行时错误
    print("\n测试 2: Python 运行时错误")
    code = "x = 10 / 0"  # 除零错误
    success, output, _ = execute_code_multi_language(code, Language.PYTHON)
    print(f"状态: {'✓ 成功' if success else '✗ 失败'}")
    print(f"错误信息:\n{output}")


def main():
    """主函数"""
    print_banner()

    print(f"支持的语言: {', '.join(get_supported_languages())}")
    print("\n请选择演示:")
    print("  1. Python 演示")
    print("  2. JavaScript 演示")
    print("  3. C++ 演示")
    print("  4. Go 演示")
    print("  5. 自动语言检测")
    print("  6. 多语言对比")
    print("  7. 错误处理")
    print("  8. 运行所有演示")

    choice = input("\n> ").strip()

    demos = {
        '1': demo_python,
        '2': demo_javascript,
        '3': demo_cpp,
        '4': demo_go,
        '5': demo_auto_detect,
        '6': demo_comparison,
        '7': demo_error_handling,
    }

    if choice == '8':
        # 运行所有演示
        for demo_func in demos.values():
            demo_func()
            input("\n按 Enter 继续...")
    elif choice in demos:
        demos[choice]()
    else:
        print("无效选择")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
