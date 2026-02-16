import os
from datetime import datetime
from typing import Annotated, TypedDict
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()

# ========================= CONFIG =========================
MODEL = "qwen3-coder:30b"

UE_PROJECT_PATH = os.getenv("UE_PROJECT_PATH")
OUTPUT_FOLDER   = os.getenv("OUTPUT_FOLDER")

if not UE_PROJECT_PATH:
    raise ValueError("UE_PROJECT_PATH is not set in .env — please create .env from .env.example and fill it in.")
if not OUTPUT_FOLDER:
    raise ValueError("OUTPUT_FOLDER is not set in .env — please create .env from .env.example and fill it in.")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

llm = ChatOllama(model=MODEL, temperature=0.3, num_ctx=128000)

# ========================= SYSTEM PROMPT (UE 5.7.3) =========================
SYSTEM_PROMPT = """You are an expert Unreal Engine 5.7.3 Python scripter.
Your job is to generate complete, ready-to-run .py scripts that create coherent "creative kits" of Blueprints.
A kit = multiple related Blueprints (Animation BP + Gameplay BP + Material Instance + Actor BP) that work together out of the box.

Use ONLY the official Unreal Python API (unreal.BlueprintFactory, SubobjectDataSubsystem, BlueprintEditorLibrary, etc.).
Always:
- Create assets under /Game/ paths
- Compile every blueprint
- Add clear comments
- Make everything modular and reusable
- Output ONE single .py file that the user can drop into their UE project and run from the Python console.

Current date: February 2026. UE version: 5.7.3."""

# ========================= TOOL =========================
def save_kit_script(code: str, kit_name: str) -> str:
    """Save the generated script to disk."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{kit_name.lower().replace(' ', '_')}_{timestamp}.py"
    path = os.path.join(OUTPUT_FOLDER, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    return f"Saved to: {path}"

tools = [save_kit_script]
tool_node = ToolNode(tools)

# ========================= GRAPH =========================
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def agent_node(state: AgentState):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm.bind_tools(tools).invoke(messages)
    return {"messages": [response]}

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    lambda x: "tools" if x["messages"][-1].tool_calls else END 
)
workflow.add_edge("tools", "agent")

app = workflow.compile(checkpointer=MemorySaver())

# ========================= RUN =========================
def run_agent(prompt: str, kit_name: str = "MyKit"):
    print("🚀 Starting UE Kit Agent (streaming mode)...")
    config = {"configurable": {"thread_id": kit_name}}
    
    # Force tool use in system prompt (critical for Qwen)
    global SYSTEM_PROMPT
    SYSTEM_PROMPT += "\n\nCRITICAL: Generate the FULL .py script in your mind, then IMMEDIATELY call the save_kit_script tool with the complete code. Do NOT output any partial code or explanations first — just the tool call."
    
    for event in app.stream(
        {"messages": [HumanMessage(content=prompt)]},
        config=config,
        stream_mode="values"  # Live state updates
    ):
        if "messages" in event and event["messages"]:
            last = event["messages"][-1]
            if hasattr(last, "tool_calls") and last.tool_calls:
                print(f"🛠️  TOOL CALL: {last.tool_calls[0]['name']} (args: {last.tool_calls[0]['args']})")
            elif hasattr(last, "content") and last.content.strip():
                print(f"🤖 AGENT: {last.content[:300]}...")  # Truncated for speed
            else:
                print(f"📡 EVENT: {type(last).__name__}")
    
    # Final save/print
    final_state = app.get_state(config)
    last_msg = final_state.values["messages"][-1]
    if hasattr(last_msg, "content") and "Saved to:" in last_msg.content:
        print("\n✅ " + last_msg.content)
    else:
        print("\nGenerated code:\n")
        print(last_msg.content)
        save_kit_script(last_msg.content, kit_name)