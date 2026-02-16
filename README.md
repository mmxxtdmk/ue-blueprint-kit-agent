# Unreal Engine Blueprint Kit Agent

**A fully local, open-source AI agent that generates complete, reusable "creative kits" of Unreal Engine Blueprints from natural language.**

Built for Unreal Engine 5.7.3 (February 2026). Runs 100% on your machine using Ollama + LangGraph. No Docker, no paid APIs, no cloud.

Created by @mmxxtdmk — feel free to fork, customize, and push the state of the art for creative-tool agents.

## Features
- Natural language → coherent Blueprint kits (Animation BP + Gameplay BP + Materials + Actors that work together)
- Generates ready-to-run `.py` scripts using the official Unreal Python API
- Runs locally on your GPU (RTX 5090 tested. GPU acceleration via Ollama)
- Hierarchical agent loop with memory and tool use
- Outputs land directly in your UE project (configurable)
- Fully open source — MIT licensed
- Easy to extend (add RAG, self-validation, multi-agent refinement, etc.)

## Tech Stack
- **LLM**: Ollama (qwen3-coder:30b or better. devstral does not work for this purpose)
- **Framework**: LangGraph + LangChain
- **Unreal Integration**: Official Unreal Python API (UE 5.7.3)
- **Python**: 3.10+

## Prerequisites
- Windows 11 Pro (tested)
- Ollama running (Installed on your machine)
- Unreal Engine 5.7.3 Editor
- Python 3.10+ (comes with UE or use system Python)
- Git

## Quick Start (5–10 minutes)

### 1. Clone / Setup the repo
```powershell
mkdir C:\Projects\ue-blueprint-kit-agent
cd C:\Projects\ue-blueprint-kit-agent
git clone https://github.com/mmxxtdmk/ue-blueprint-kit-agent.git .
```

### 2. Create virtual environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Pull the model (once)
```powershell
ollama pull qwen3-coder:30b   # devstral will not generate code for this use case.
```

### 5. Configure .env (optional but recommended)
Create a file called .env in the root:
```env
UE_PROJECT_PATH=C:/UnrealProjects/MyProject
OUTPUT_FOLDER=./generated_kits
```

### 6. Run your first kit
```powershell
python run_agent.py "Create a complete modular third-person animation + gameplay + material kit for UE 5.7.3. Include a Character Blueprint with animation graph, a simple weapon actor, and a reusable material instance system."
```

The script will appear in generated_kits/ (or directly in your UE project if you set UE_PROJECT_PATH).

### 7. Use in Unreal
- Copy the generated .py into your UE project (e.g. Content/Python)
- Open Unreal Editor → Window → Python Console
- Run: `exec(open(r"path\to\your_script.py").read())`

## Project Structure

ue-blueprint-kit-agent/

├── agent.py              # Core LangGraph agent

├── run_agent.py          # CLI entry point

├── requirements.txt

├── .env.example

├── .gitignore

├── LICENSE

└── generated_kits/       # Output folder (gitignored)

## How to Contribute
- Fork the repo
- Create a feature branch (`git checkout -b feature/amazing-thing`)
- Commit and push
- Open a PR

## Ideas for SOTA contributions:
- Add RAG over UE Python docs + your own Blueprints
- Self-validation loop (run script → capture compile errors → auto-fix)
- Multi-agent refinement (Requirements → Architect → Generator → Validator)
- Evaluation suite (compile success rate, artist usefulness scores)
- Support for Control Rig, Niagara, etc.

## License
- MIT License — see (LICENSE)

## Acknowledgments
- Ollama team
- LangGraph / LangChain community
- Everyone building creative-tool agents in 2026

Made with <3 for the Unreal community. Let’s make Blueprint generation 10× faster.