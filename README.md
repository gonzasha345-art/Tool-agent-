# tool-agent

Minimal, dependency-free tool-calling agent in Python.

- `agent/tools.py` – tool registry (`@tool` decorator; calculator, current_time, github_repo_info)
- `agent/core.py` – loop: model -> tool calls -> results -> model, until a final answer

```bash
export OPENAI_API_KEY=...   # optional: OPENAI_BASE_URL, AGENT_MODEL
python main.py "What is 12*(3+4)?"
pip install pytest && pytest   # tests use a fake LLM, no key needed
```

Add a tool by decorating a function with `@tool(description, parameters)`.
