import json

from agent.core import run_agent
from agent.tools import run_tool


def test_calculator_and_errors():
    assert run_tool("calculator", {"expression": "2*(3+4)"}) == "14"
    assert run_tool("calculator", {"expression": "__import__('os')"}).startswith("error")
    assert run_tool("nope", {}).startswith("error")


def test_agent_loop_calls_tool_then_answers():
    seen = []

    def fake_llm(messages, tools):
        seen.append(len(messages))
        if messages[-1]["role"] == "tool":
            return {"role": "assistant", "content": f"Answer: {messages[-1]['content']}"}
        return {"role": "assistant", "content": None, "tool_calls": [
            {"id": "1", "type": "function",
             "function": {"name": "calculator",
                          "arguments": json.dumps({"expression": "6*7"})}}]}

    assert run_agent("6*7?", llm=fake_llm, log=lambda *_: None) == "Answer: 42"
