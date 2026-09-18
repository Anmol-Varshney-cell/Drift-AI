# Junior AI Engineer — Take-Home Assignments Submission

This repository contains production-ready implementations for all three take-home assignments for the **Junior AI Engineer** role, built using **LangGraph** (`langgraph` >= 1.2, `langchain-core` >= 1.6).

---

## 🏛️ Framework Decision: Why LangGraph?

The instructions allow selecting either **LangGraph** or **LangChain** (*"All three assignments must be built using both LangGraph or LangChain — at least any one of the frameworks, without fail"*). 

We selected **LangGraph** across all three assignments for the following architectural reasons:
1. **Cyclical State Graphs vs. Linear Chains**: Assignment 1 tests autonomous planning loops (`Agent ➔ Tool ➔ Observe ➔ Agent`), max tool call limits, and error recovery. LangGraph's cyclic state graphs natively handle loop conditions, dynamic routing, and stopping decisions.
2. **Deterministic Agent Handoffs**: Assignment 2 tests a clean two-agent pipeline (`Worker ➔ Reviewer`) with explicit rubric evaluation and token tracking without infinite negotiation loops. LangGraph models multi-node pipelines with typed state contracts cleanly.
3. **Official Built-in Checkpointing**: Assignment 3 explicitly mandates: *"use LangGraph's built-in state/checkpointing rather than hand-rolling your own"*. LangGraph provides `SqliteSaver`, enabling disk-persisted checkpointing across process restarts with session `thread_id` management.

---

## 📂 Repository Structure

```
Drift.AI/
├── README.md                          # Global repository overview and quickstart
├── requirements.txt                   # Dependency definitions
├── .env.example                       # Environment configuration template
├── .gitignore                         # Standard git ignore rules
├── shared/
│   └── llm.py                         # Multi-provider LLM factory (Gemini, Groq, OpenAI, Mock)
├── assignment-1/
│   ├── README.md                      # Detailed design, tools, and execution guide
│   ├── agent.py                       # Autonomous LangGraph research agent
│   ├── tools.py                       # 3 domain tools with injectable failure modes
│   ├── run.py                         # CLI runner (--clean, --fail-tool)
│   └── transcripts/
│       ├── transcript_clean_run.md    # Transcript 1: Clean run (4/6 tools used, final synthesis)
│       └── transcript_failure_run.md  # Transcript 2: 503 timeout caught & autonomously recovered
├── assignment-2/
│   ├── README.md                      # Multi-agent architecture and 5-point evaluation rubric
│   ├── multi_agent.py                 # Worker Agent ➔ Reviewer Agent LangGraph chain
│   ├── rubric.py                      # 5 concrete, non-vague review criteria
│   ├── run.py                         # CLI runner (--mode approved, --mode rejected)
│   └── transcripts/
│       ├── transcript_approved.md     # Transcript 1: High quality code approved by Reviewer
│       └── transcript_rejected.md     # Transcript 2: Flawed code rejected with itemized grounds
└── assignment-3/
    ├── README.md                      # Checkpointing architecture, stop/resume, and self-check
    ├── resumable_agent.py             # LangGraph batch agent with SqliteSaver checkpointer
    ├── dataset.py                     # 4 technical incident postmortems
    ├── run.py                         # CLI runner (--demo-stop-resume, --demo-self-check)
    └── transcripts/
        ├── transcript_stop_resume.md  # Transcript 1: Stopped partway ➔ resumed skipping finished
        └── transcript_self_check.md   # Transcript 2: Self-check catching deliberate blank item
```

---

## 📊 Summary of Assignments & Deliverables

| Assignment | Core Capability Tested | Deliverable Transcripts | Key Features & Constraints Met |
|---|---|---|---|
| **[Assignment 1](assignment-1/)** | Autonomous Tool-Using Research Agent | • [`transcript_clean_run.md`](assignment-1/transcripts/transcript_clean_run.md)<br>• [`transcript_failure_run.md`](assignment-1/transcripts/transcript_failure_run.md) | • Dynamic planning (no fixed script)<br>• 3 distinct tools (docs, latency SLA, cost)<br>• Autonomous stopping (no fixed iterations)<br>• Max 6 tool calls budget enforced in state<br>• Structured reasoning trace (`Thought`, `Decision`, `Why`, `Action`, `Observation`)<br>• Detects 503 tool timeout and adapts without crashing |
| **[Assignment 2](assignment-2/)** | Multi-Agent Task with Review | • [`transcript_approved.md`](assignment-2/transcripts/transcript_approved.md)<br>• [`transcript_rejected.md`](assignment-2/transcripts/transcript_rejected.md) | • Worker (Agent A) ➔ Reviewer (Agent B)<br>• 5 concrete evaluation criteria (correctness, concurrency, edge cases, docstrings, ergonomics)<br>• No negotiation loop (single review pass)<br>• Reports total LLM calls and token metrics |
| **[Assignment 3](assignment-3/)** | Resumable Agent with Basic Self-Check | • [`transcript_stop_resume.md`](assignment-3/transcripts/transcript_stop_resume.md)<br>• [`transcript_self_check.md`](assignment-3/transcripts/transcript_self_check.md) | • Processes 4 incident reports one at a time<br>• LangGraph `SqliteSaver` disk checkpointing<br>• Programmatic stop at item 2 ➔ re-run skips completed items<br>• Self-check node re-reads results and catches corrupted/empty output<br>• Reports total LLM calls |

---

## ⚡ Quickstart Guide

### 1. Environment Setup
Clone the repository and set up a virtual environment using Python 3.11+:
```bash
# Clone the repository
git clone <repo_url>
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

### 2. Running Out-of-the-Box (Zero-Configuration)
All scripts include an autonomous deterministic fallback mode. Anyone cloning the repository can immediately execute all tests without requiring external API keys or incurring costs:

```bash
# Test Assignment 1: Clean run and failure run
python assignment-1/run.py
python assignment-1/run.py --fail-tool

# Test Assignment 2: Approved run and rejected run
python assignment-2/run.py --mode approved
python assignment-2/run.py --mode rejected

# Test Assignment 3: Stop-and-resume workflow and self-check validation
python assignment-3/run.py --demo-stop-resume
python assignment-3/run.py --demo-self-check
```

### 3. Optional: Live LLM Execution (Google Gemini, Groq, OpenAI)
To connect live model providers, copy `.env.example` to `.env` and set your key:
```bash
cp .env.example .env
```
Supported providers:
- **Google AI Studio (Gemini)**: Recommended default (`GEMINI_API_KEY`)
- **Groq**: Free fast inference (`GROQ_API_KEY`)
- **OpenAI**: (`OPENAI_API_KEY`)

Pass `--provider gemini` or `--provider groq` to any runner script.

---

## 📌 Assumptions Stated (per Guidelines)
- **Assignment 1**: In the event of a downstream microservice failure (503 timeout on latency calculator), we assumed the agent should prioritize avoiding repeated failing calls that burn the 6-call tool budget, instead pivoting to architectural documentation and hardware cost estimation to complete the SLA recommendation analytically.
- **Assignment 2**: For thread-safety evaluation of the Token Bucket algorithm, we assumed state changes (`tokens`, `last_updated`) must be guarded by a mutex (`threading.Lock` or `threading.RLock`) to prevent race conditions during concurrent bursts.
- **Assignment 3**: For checkpointing persistence across process terminations, we assumed disk-backed SQLite checkpointing (`SqliteSaver`) rather than in-memory storage (`MemorySaver`), ensuring state is preserved even if the process is killed via `exit()` or `Ctrl+C`.
