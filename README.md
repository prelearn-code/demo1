# 🤖 Coding Agent Local - Ollama Demo

基于 **LangGraph** + **Ollama (Qwen2.5-Coder-7B)** 的本地编程助手

这是一个符合软件工程规范的模块化项目，专门为本地 Ollama 适配，能够自动生成代码、执行并调试。

## ✨ 特性

- 🔄 **自动迭代**: 代码生成 -> 执行 -> 错误反思 -> 重新生成
- 🏗️ **模块化设计**: 遵循关注点分离原则，易于扩展
- 🎯 **针对 7B 模型优化**: 简洁的 Prompt 设计，适合小参数模型
- 🔧 **完全本地运行**: 无需 API Key，保护隐私

## 📁 项目结构

```
coding-agent-local/
├── .env                     # 环境变量配置
├── requirements.txt         # Python 依赖
├── main.py                  # 项目入口
└── src/
    ├── config.py            # 全局配置
    ├── llm/                 # LLM 客户端封装
    │   └── client.py
    ├── agent/               # Agent 核心逻辑
    │   ├── state.py         # 状态定义
    │   ├── prompts.py       # Prompt 模板
    │   ├── nodes.py         # 节点逻辑
    │   └── graph.py         # 工作流构建
    └── tools/               # 工具层
        ├── sandbox.py       # 代码执行
        └── parser.py        # 输出解析
```

## 🚀 快速开始

### 1. 环境准备

#### 安装 Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: 访问 https://ollama.com/download
```

#### 启动 Ollama 服务

```bash
ollama serve
```

#### 下载模型

```bash
ollama pull qwen2.5-coder:7b
```

### 2. 安装 Python 依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

编辑 `.env` 文件 (已包含默认配置):

```ini
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b
MAX_ITERATIONS=5
TEMPERATURE=0
```

### 4. 运行 Demo

```bash
python main.py
```

## 💡 使用示例

运行后会看到交互界面:

```
╔═══════════════════════════════════════════════════╗
║      🤖 Coding Agent Local - Ollama Demo         ║
║      基于 LangGraph + Qwen2.5-Coder-7B            ║
╚═══════════════════════════════════════════════════╝

示例任务:
  1. 写一个函数计算斐波那契数列的第n项
  2. 生成1-100之间的所有质数
  3. 实现一个简单的计算器(支持加减乘除)

请输入你的编程任务 (或输入数字选择示例):
>
```

输入任务描述或选择示例，Agent 会自动:
1. 生成 Python 代码
2. 执行代码
3. 如果失败，分析错误并重新生成
4. 最多迭代 5 次

## 🔧 核心组件说明

### 1. LLM 客户端 (`src/llm/client.py`)

封装 `ChatOllama`，提供单例模式的 LLM 实例:

```python
from src.llm import get_llm

llm = get_llm()  # 自动加载配置
```

### 2. Agent 状态 (`src/agent/state.py`)

定义 LangGraph 的状态结构:

```python
class AgentState(TypedDict):
    messages: List[BaseMessage]    # 对话历史
    code: Optional[str]             # 当前代码
    execution_result: Optional[str] # 执行结果
    error: Optional[str]            # 错误信息
    iterations: int                 # 迭代次数
```

### 3. 工作流 (`src/agent/graph.py`)

状态机流转:

```
START -> coder -> executor -> [判断]
                                ├─> END (成功)
                                └─> reflector -> coder (失败,继续迭代)
```

### 4. 代码执行 (`src/tools/sandbox.py`)

使用 `subprocess` 执行代码 (⚠️ 仅用于演示，不安全):

```python
from src.tools import execute_code

success, output = execute_code("print('Hello')")
```

## ⚙️ 配置说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `OLLAMA_BASE_URL` | Ollama 服务地址 | `http://localhost:11434` |
| `OLLAMA_MODEL` | 模型名称 | `qwen2.5-coder:7b` |
| `MAX_ITERATIONS` | 最大迭代次数 | `5` |
| `TEMPERATURE` | 生成温度 (0=确定性) | `0` |

## 🛡️ 安全警告

**当前版本使用 `subprocess` 直接执行代码，存在安全风险！**

生产环境请使用以下方案:
- Docker 容器隔离
- E2B Sandbox
- Pyodide (浏览器沙箱)

## 📝 常见问题

### Q: 模型下载慢或失败？

```bash
# 使用国内镜像 (需配置环境变量)
export OLLAMA_HOST=https://mirror.example.com
ollama pull qwen2.5-coder:7b
```

### Q: 连接 Ollama 失败？

检查服务是否启动:

```bash
curl http://localhost:11434/api/tags
```

### Q: 代码执行超时？

修改 `.env`:

```ini
# 在 sandbox.py 中默认 10 秒，可以在代码中调整 timeout 参数
```

## 🔄 工作流程示例

```
用户输入: "生成1-100之间的质数"

[Coder] 正在生成代码...
[Coder] 代码已生成 (迭代 1)
```python
for num in range(2, 101):
    is_prime = True
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            is_prime = False
            break
    if is_prime:
        print(num)
```

[Executor] 正在执行代码...
[Executor] ✓ 执行成功
输出:
2
3
5
7
...
97

✅ 成功!
```

## 📚 技术栈

- **LangChain/LangGraph**: 编排框架
- **Ollama**: 本地 LLM 服务
- **Qwen2.5-Coder-7B**: 代码生成模型
- **Pydantic**: 配置管理
- **Python 3.8+**: 运行环境

## 🚧 路线图

- [ ] 支持 Docker 沙箱执行
- [ ] 添加代码测试生成
- [ ] 支持多轮对话
- [ ] 可视化工作流 (LangGraph Studio)
- [ ] 支持更多模型 (DeepSeek-Coder, CodeLlama)

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

---

**⚡️ 开始你的本地 AI 编程之旅吧!**
