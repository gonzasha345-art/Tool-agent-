import sys

from agent.core import run_agent

if __name__ == "__main__":
    print(run_agent(" ".join(sys.argv[1:]) or "What is 12*(3+4) and what time is it?"))
