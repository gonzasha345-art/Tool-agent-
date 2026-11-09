"""Tool registry: functions the agent can call, with JSON schemas."""
import ast
import json
import operator
import urllib.request
from datetime import datetime, timezone

TOOLS = {}


def tool(description, parameters):
    def deco(fn):
        TOOLS[fn.__name__] = {
            "fn": fn,
            "schema": {
                "type": "function",
                "function": {
                    "name": fn.__name__,
                    "description": description,
                    "parameters": {"type": "object", "properties": parameters,
                                   "required": list(parameters)},
                },
            },
        }
        return fn
    return deco


_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
        ast.USub: operator.neg}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")


@tool("Evaluate an arithmetic expression, e.g. '2*(3+4)'.",
      {"expression": {"type": "string"}})
def calculator(expression):
    return str(_eval(ast.parse(expression, mode="eval").body))


@tool("Get the current UTC date and time.", {})
def current_time():
    return datetime.now(timezone.utc).isoformat()


@tool("Fetch public info for a GitHub repo, given 'owner/name'.",
      {"repo": {"type": "string"}})
def github_repo_info(repo):
    with urllib.request.urlopen(f"https://api.github.com/repos/{repo}", timeout=10) as r:
        d = json.load(r)
    return json.dumps({k: d.get(k) for k in
                       ("full_name", "description", "stargazers_count", "language", "html_url")})


def run_tool(name, arguments):
    """Execute a tool by name; errors are returned as text so the model can recover."""
    if name not in TOOLS:
        return f"error: unknown tool {name}"
    try:
        return TOOLS[name]["fn"](**arguments)
    except Exception as e:  # noqa: BLE001
        return f"error: {e}"
