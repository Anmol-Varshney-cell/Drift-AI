# Junior AI Engineer — Take-Home Assignments Submission

This repository contains production-ready implementations for the take-home assignments for the **Junior AI Engineer** role, built using **LangGraph** (`langgraph` >= 1.2, `langchain-core` >= 1.6).

Per the evaluation guidelines (*"There are 3 total at least two assignments need to be submitted"*), this submission provides complete, verified solutions and transcripts for **Assignment 1** and **Assignment 2**. 
# URL-*https://drift-ai-1.streamlit.app/*  

---

## 🏛️ Framework Decision: Why LangGraph?

The instructions specify using either **LangGraph** or **LangChain** (*"All three assignments must be built using both LangGraph or LangChain — at least any one of the frameworks, without fail"*).

We selected **LangGraph** for both assignments:
1. **Assignment 1 (Tool-Using Research Agent)**: Cyclical State Graphs (`planner ➔ tool_executor ➔ planner`) natively model dynamic planning loops, strict tool call budget enforcement (<= 6 calls), and adaptive recovery from tool timeouts without relying on hardcoded scripts.
2. **Assignment 2 (Multi-Agent Task with Review)**: Multi-agent state pipelines (`WorkerAgent ➔ ReviewerAgent`) ensure clean handoffs, objective 5-point rubric grading, and strict single-review termination without infinite negotiation loops.

---

## 📂 Repository Structure

```
Drift.AI/
├── README.md                          # Global repository overview and quickstart
├── app.py                             # Interactive Streamlit dashboard for both assignments
├── requirements.txt                   # Dependency definitions
├── .env.example                       # Environment configuration template
├── .gitignore                         # Standard git ignore rules
├── shared/
│   └── llm.py                         # Multi-provider LLM factory (Gemini, Groq, OpenAI, Mock)
├── assignment-1/                      # Assignment 1: Tool-Using Research Agent
│   ├── README.md                      # Detailed design, tools, and execution guide
│   ├── app.py                         # Dedicated Streamlit app for Assignment 1
│   ├── agent.py                       # Autonomous LangGraph research agent
│   ├── tools.py                       # 3 domain tools with injectable failure modes
│   ├── run.py                         # CLI runner (--clean, --fail-tool)
│   └── transcripts/
│       ├── transcript_clean_run.md    # Transcript 1: Clean run (4/6 tools used, final synthesis)
│       └── transcript_failure_run.md  # Transcript 2: 503 timeout caught & autonomously recovered
└── assignment-2/                      # Assignment 2: Multi-Agent Task with Review
    ├── README.md                      # Multi-agent architecture and 5-point evaluation rubric
    ├── multi_agent.py                 # Worker Agent ➔ Reviewer Agent LangGraph chain
    ├── rubric.py                      # 5 concrete, non-vague review criteria
    ├── run.py                         # CLI runner (--mode approved, --mode rejected)
    └── transcripts/
        ├── transcript_approved.md     # Transcript 1: High quality code approved by Reviewer
        └── transcript_rejected.md     # Transcript 2: Flawed code rejected with itemized grounds
```

---

## 📊 Summary of Assignments & Deliverables

| Assignment | Core Capability Tested | Deliverable Transcripts | Key Features & Constraints Met |
|---|---|---|---|
| **[Assignment 1](assignment-1/)** | Autonomous Tool-Using Research Agent | • [`transcript_clean_run.md`](assignment-1/transcripts/transcript_clean_run.md)<br>• [`transcript_failure_run.md`](assignment-1/transcripts/transcript_failure_run.md) | • Dynamic planning (no fixed script)<br>• 3 distinct tools (docs, latency SLA, cost)<br>• Autonomous stopping (no fixed iterations)<br>• Max 6 tool calls budget enforced in state<br>• Structured reasoning trace (`Thought`, `Decision`, `Why`, `Action`, `Observation`)<br>• Detects 503 tool timeout and adapts without crashing |
| **[Assignment 2](assignment-2/)** | Multi-Agent Task with Review | • [`transcript_approved.md`](assignment-2/transcripts/transcript_approved.md)<br>• [`transcript_rejected.md`](assignment-2/transcripts/transcript_rejected.md) | • Worker (Agent A) ➔ Reviewer (Agent B)<br>• 5 concrete evaluation criteria (correctness, concurrency, edge cases, docstrings, ergonomics)<br>• No negotiation loop (single review pass)<br>• Reports total LLM calls and token metrics |

---

## ⚡ Quickstart Guide

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/Anmol-Varshney-cell/Drift-AI.git
cd Drift.AI

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running CLI Commands
All scripts include an autonomous deterministic fallback mode so they run out of the box with zero external API keys:

```bash
# Test Assignment 1: Clean run and failure run
python assignment-1/run.py
python assignment-1/run.py --fail-tool

# Test Assignment 2: Approved run and rejected run
python assignment-2/run.py --mode approved
python assignment-2/run.py --mode rejected
```

### 3. Running the Streamlit Web Application
```bash
# Option A: Run the unified portal (Assignment 1 & 2)
streamlit run app.py

# Option B: Run only Assignment 1
streamlit run assignment-1/app.py
```

### 4. Optional: Live LLM Execution (Google Gemini, Groq, OpenAI)
To connect live model providers, copy `.env.example` to `.env` and configure your API key:
```bash
cp .env.example .env
```
Supported providers:
- **Google AI Studio (Gemini)**: Recommended default (`GEMINI_API_KEY`)
- **Groq**: Free fast inference (`GROQ_API_KEY`)
- **OpenAI**: (`OPENAI_API_KEY`)
