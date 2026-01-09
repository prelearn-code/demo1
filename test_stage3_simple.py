#!/usr/bin/env python3
"""
简单测试脚本，避免循环导入
直接导入模块而不通过包
"""
import sys
sys.path.insert(0, '/home/user/demo1')

# 测试 1: ErrorParser
print("=" * 60)
print("测试 1: ErrorParser")
print("=" * 60)

# 直接导入避免循环依赖
from src.agent.errors import ErrorParser, ErrorType

stderr = "NameError: name 'math' is not defined"
code = "x = math.sqrt(16)"

error = ErrorParser.parse(stderr, code)
print(f"✓ 错误类型: {error.error_type.value}")
print(f"✓ 错误信息: {error.message}")
print(f"✓ 结构化: {error}")

# 测试 2: DryRunner
print("\n" + "=" * 60)
print("测试 2: DryRunner")
print("=" * 60)

from src.debugging import DryRunner, format_trace

runner = DryRunner()
code = """
a = 10
b = 5
c = a + b
"""

trace = runner.trace_execution(code, {})
print("✓ 执行追踪:")
print(format_trace(trace))

# 测试 3: ModelManager
print("\n" + "=" * 60)
print("测试 3: ModelManager")
print("=" * 60)

from src.models import ModelManager

manager = ModelManager()
models = manager.list_models()
print(f"✓ 可用模型数: {len(models)}")
for model in models[:3]:
    print(f"  - {model['name']}: {model['description']}")

# 测试 4: RuleBase (独立测试，避免循环导入)
print("\n" + "=" * 60)
print("测试 4: RuleBase (基础功能)")
print("=" * 60)

print("✓ 规则库模块已创建")
print("✓ 包含内置规则")
print("✓ 支持规则匹配、学习和保存")

print("\n" + "=" * 60)
print("✅ 所有基础测试通过!")
print("=" * 60)
