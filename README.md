# Coding Agent Local (Qwen2.5-Coder-7B)

A modular starter template for running a local coding agent powered by **Ollama** with the **Qwen2.5-Coder-7B** model. The repository separates configuration, prompt strategy, agent graph, and tooling to simplify fine-tuning and iteration.

## Project layout
```
coding-agent-local/
├── .env.example            # Sample environment variables
├── requirements.txt        # Python dependencies
├── main.py                 # Entry point for running the agent loop
├── notebooks/
│   └── architecture_test.ipynb
└── src/
    ├── config.py           # Pydantic settings
    ├── llm/
    │   └── client.py       # ChatOllama singleton wrapper
    ├── agent/
    │   ├── state.py        # AgentState definition
    │   ├── graph.py        # LangGraph topology
    │   ├── nodes.py        # Node logic for coder/reflector/executor
    │   └── prompts.py      # Prompt templates tailored for 7B
    └── tools/
        ├── sandbox.py      # Local executor (subprocess-based)
        └── parser.py       # Output parser for cleaning code blocks
```

## Quickstart
1. Create and activate a virtual environment.
2. Copy `.env.example` to `.env` and adjust values if needed.
3. Install dependencies: `pip install -r requirements.txt`.
4. Validate connectivity: `python -c "from langchain_ollama import ChatOllama; print(ChatOllama(model='qwen2.5-coder:7b').invoke('print(\"hello\")').content)"`.
5. Run the agent: `python main.py "build a hello world script"`.

## Notes
- The agent loop is intentionally lightweight for 7B models and uses a concise role-based prompt.
- Execution happens locally via `subprocess`. For stricter isolation, extend `src/tools/sandbox.py` with Docker support.
