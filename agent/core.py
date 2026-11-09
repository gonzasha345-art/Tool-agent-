"""Tool-calling loop against an OpenAI-compatible chat completions API."""
import json
import os
import urllib.request

from .tools import TOOLS, run_tool


def chat(messages, tools):
    """Call the LLM. Set OPENAI_API_KEY (and optionally OPENAI_BASE_URL / AGENT_MODEL)."""
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps({"model": os.environ.get("AGENT_MODEL", "gpt-4o-mini"),
                         "messages": messages, "tools": tools}).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["choices"][0]["message"]


def run_agent(task, llm=chat, max_steps=8, log=print):
    messages = [
        {"role": "system", "content": "You are a helpful agent. Use tools when useful."},
        {"role": "user", "content": task},
    ]
    schemas = [t["schema"] for t in TOOLS.values()]
    for _ in range(max_steps):
        msg = llm(messages, schemas)
        messages.append(msg)
        calls = msg.get("tool_calls")
        if not calls:
            return msg.get("content", "")
        for c in calls:
            name = c["function"]["name"]
            args = json.loads(c["function"]["arguments"] or "{}")
            log(f"[tool] {name}({args})")
            result = run_tool(name, args)
            messages.append({"role": "tool", "tool_call_id": c["id"], "content": str(result)})
    return "Stopped: max steps reached."
