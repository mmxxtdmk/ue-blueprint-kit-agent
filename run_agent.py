from agent import run_agent
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_agent.py \"your natural language prompt\"")
        sys.exit(1)
    prompt = " ".join(sys.argv[1:])
    run_agent(prompt, kit_name="CreativeKit")