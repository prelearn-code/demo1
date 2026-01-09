# 🌍 多语言支持指南

## 概述

项目现在支持**多种编程语言**的代码执行，不仅限于 Python！

## 支持的语言

| 语言 | Docker 镜像 | 状态 |
|------|------------|------|
| **Python** | `python:3.11-alpine` | ✅ 原生支持 |
| **JavaScript** | `node:18-alpine` | ✅ 新增 |
| **TypeScript** | `node:18-alpine` + ts-node | ✅ 新增 |
| **Java** | `openjdk:17-alpine` | ✅ 新增 |
| **C++** | `gcc:12-alpine` | ✅ 新增 |
| **C** | `gcc:12-alpine` | ✅ 新增 |
| **Go** | `golang:1.21-alpine` | ✅ 新增 |
| **Rust** | `rust:1.75-alpine` | ✅ 新增 |

## 快速开始

### 1. 拉取所需 Docker 镜像

```bash
# Python (已有)
docker pull python:3.11-alpine

# JavaScript/TypeScript
docker pull node:18-alpine

# Java
docker pull openjdk:17-alpine

# C/C++
docker pull gcc:12-alpine

# Go
docker pull golang:1.21-alpine

# Rust
docker pull rust:1.75-alpine
```

### 2. 运行多语言演示

```bash
python demo_multi_language.py
```

## 使用方法

### 方式一：自动语言检测

```python
from src.tools.multi_language_sandbox import execute_code_multi_language

# 代码会自动检测语言
code = """
console.log('Hello from JavaScript!');
"""

success, output, language = execute_code_multi_language(code)
print(f"检测到的语言: {language.value}")
print(f"输出: {output}")
```

### 方式二：指定语言

```python
from src.tools.multi_language_sandbox import (
    execute_code_multi_language,
    Language
)

code = """
#include <iostream>
using namespace std;

int main() {
    cout << "Hello from C++!" << endl;
    return 0;
}
"""

success, output, language = execute_code_multi_language(
    code,
    language=Language.CPP  # 明确指定语言
)
```

## 语言检测规则

系统通过代码特征自动检测语言：

### Python
- 关键字: `def`, `import`, `from ... import`, `print(`

### JavaScript
- 关键字: `const`, `let`, `var`, `function`, `console.log`, `=>`

### TypeScript
- JavaScript 特征 + 类型注解: `: string`, `interface`, `type`

### Java
- 关键字: `public class`, `public static void main`, `System.out.print`

### C++
- 关键字: `#include <iostream>`, `std::cout`, `namespace std`

### C
- 关键字: `#include <stdio.h>`, `printf`, `scanf`

### Go
- 关键字: `package main`, `func main`, `fmt.Print`

### Rust
- 关键字: `fn main`, `println!`, `use std::`

## 代码执行流程

```
代码 → 语言检测 → 选择镜像 → Docker 容器 → 执行 → 结果
```

### 编译型语言（Java, C++, C, Rust）
1. 将代码写入临时文件
2. 编译代码
3. 执行编译后的程序

### 解释型语言（Python, JavaScript, Go）
1. 直接通过解释器执行

## 示例

### Python - 斐波那契数列

```python
code = """
def fibonacci(n):
    a, b = 0, 1
    for i in range(n):
        a, b = b, a + b
    return a

print(fibonacci(10))
"""

success, output, _ = execute_code_multi_language(code)
```

### JavaScript - 数组操作

```javascript
code = """
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(x => x * 2);
console.log(doubled);
"""

success, output, _ = execute_code_multi_language(code)
```

### C++ - 排序算法

```cpp
code = """
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    vector<int> nums = {5, 2, 8, 1, 9};
    sort(nums.begin(), nums.end());

    for (int num : nums) {
        cout << num << " ";
    }
    cout << endl;
    return 0;
}
"""

success, output, _ = execute_code_multi_language(code, Language.CPP)
```

### Go - 并发示例

```go
code = """
package main

import (
    "fmt"
    "time"
)

func worker(id int) {
    fmt.Printf("Worker %d starting\\n", id)
    time.Sleep(time.Millisecond * 100)
    fmt.Printf("Worker %d done\\n", id)
}

func main() {
    for i := 1; i <= 3; i++ {
        go worker(i)
    }
    time.Sleep(time.Second)
}
"""

success, output, _ = execute_code_multi_language(code, Language.GO)
```

## 安全性

所有语言的代码执行都使用 Docker 容器隔离：
- ✅ 内存限制: 256MB
- ✅ CPU 限制: 50%
- ✅ 网络禁用
- ✅ 超时保护: 10秒
- ✅ 容器自动清理

## 集成到主程序

如果想在主程序 `main.py` 中使用多语言支持：

### 方式一：替换 sandbox（推荐用于多语言项目）

```python
# 在 src/agent/nodes.py 中
from ..tools.multi_language_sandbox import execute_code_multi_language

def executor_node(state: AgentState) -> AgentState:
    code = state.get("code", "")

    # 使用多语言执行
    success, output, language = execute_code_multi_language(code)

    state["language"] = language.value  # 记录使用的语言
    # ... 其他处理
```

### 方式二：保持兼容（推荐）

保持 `main.py` 使用原有的 Python-only 模式，多语言功能通过演示脚本使用。

## 演示脚本功能

`demo_multi_language.py` 包含 7 个演示：

1. **Python 演示** - 斐波那契数列
2. **JavaScript 演示** - 斐波那契数列
3. **C++ 演示** - 斐波那契数列
4. **Go 演示** - 斐波那契数列
5. **自动检测** - 测试语言检测功能
6. **多语言对比** - 相同功能不同实现
7. **错误处理** - 展示错误捕获

## 常见问题

### Q: 为什么需要拉取多个 Docker 镜像？

A: 每种语言需要不同的运行环境。镜像只需拉取一次，之后可以重复使用。

### Q: 编译型语言为什么更慢？

A: 需要先编译再执行。C++/Java/Rust 首次执行会慢一些，但这是正常的。

### Q: 可以添加其他语言吗？

A: 可以！在 `multi_language_sandbox.py` 的 `LANGUAGE_CONFIGS` 中添加配置即可。

### Q: TypeScript 执行失败？

A: TypeScript 需要 `ts-node`，首次执行会自动下载。如果失败，可能需要增加超时时间。

### Q: 如何查看所有支持的语言？

```python
from src.tools.multi_language_sandbox import get_supported_languages
print(get_supported_languages())
```

## 性能对比

| 语言 | 启动时间 | 执行时间 | 内存占用 |
|------|---------|---------|---------|
| Python | ~0.5s | 快 | 低 |
| JavaScript | ~0.8s | 快 | 低 |
| Go | ~1.5s | 很快 | 中 |
| C++ | ~2.5s | 最快 | 中 |
| Java | ~3.0s | 快 | 高 |
| Rust | ~3.5s | 最快 | 中 |

*注：启动时间包括编译时间（如适用）*

## 限制

1. **网络访问**: 所有语言都禁用了网络访问（安全考虑）
2. **文件系统**: 不能访问宿主机文件系统
3. **包管理**: 不支持安装额外的包/库
4. **执行时间**: 默认 10 秒超时
5. **内存**: 限制 256MB

## 扩展建议

### 添加新语言

```python
# 在 LANGUAGE_CONFIGS 中添加
Language.PHP: {
    "image": "php:8.2-alpine",
    "command": lambda code: ["php", "-r", code],
    "file_ext": ".php",
    "compile": False
}
```

### 增加超时时间

```python
success, output, lang = execute_code_multi_language(
    code,
    timeout=30  # 30 秒
)
```

### 自定义资源限制

修改 `multi_language_sandbox.py` 中的容器配置：
```python
container = client.containers.run(
    mem_limit="512m",  # 增加到 512MB
    cpu_quota=100000,  # 100% CPU
    # ...
)
```

## 总结

✅ **8 种语言**支持
✅ **自动检测**语言
✅ **Docker 隔离**安全执行
✅ **统一接口**易于使用
✅ **完整示例**快速上手

开始你的多语言编程之旅吧！🚀
