# Assignment 1: Tool-Using Research Agent

## 1. Overview
This project implements an autonomous research agent using **LangGraph**. The agent is designed to answer complex, open-ended systems design questions by dynamically planning its own research path rather than executing a hardcoded sequence of steps.

### Question Answered
> *"Compare two approaches to API caching for a read-heavy system (Redis cache-aside vs. Cloudflare CDN edge caching) and recommend an architecture for 10k req/sec with dynamic user-specific data."*

---

## 2. Tools Available to the Agent
The agent has access to **three distinct tools** tailored to systems architecture research:
1. **`architecture_docs_search(query: str)`**:
   - Searches an engineering knowledge base covering caching invalidation protocols, dynamic personalized data constraints, and VPC vs CDN architectural patterns.
2. **`latency_sla_calculator(strategy: str, req_per_sec: int, cache_hit_ratio: float)`**:
   - Computes empirical p50, p95, and p99 latency percentiles, network hop characteristics, and residual origin load at specified throughput (10,000 req/sec).
   - Can be configured to simulate a **503 service timeout** to test agentic error handling and adaptation.
3. **`cost_and_resource_estimator(strategy: str, req_per_sec: int, dataset_size_gb: float)`**:
   - Calculates monthly infrastructure expenditure (Redis RAM sizing vs Cloudflare edge worker subscriptions and bandwidth egress) for high-scale workloads.

---

## 3. Core Architecture & Compliance with Constraints

| Constraint | Implementation in LangGraph |
|---|---|
| **Autonomous Dynamic Planning** | LangGraph `StateGraph` cycles between a `planner` node and a `tool_executor` node. The planner inspects missing data and formulates decisions dynamically. |
| **Autonomous Stopping** | The agent stops when its planner determines that sufficient multi-dimensional evidence (architecture, SLA latency, cost) has been gathered to make an authoritative recommendation. |
| **Max 6 Tool Calls Limit** | The graph state tracks `tool_call_count`. If `tool_call_count >= 6`, the planner halts immediately and synthesizes a best-effort response without crashing or looping infinitely. |
| **Reasoning Trace** | Every step logs a structured trace containing **Decision**, **Rationale (Why)**, **Action Taken**, and **Observation (Result)**. |
| **Graceful Tool Failure Handling** | When `latency_sla_calculator` fails with a 503 timeout, the agent catches the failure in its observation, reasons that the service is unavailable, and adapts its plan by querying cost estimators and architecture docs instead of crashing. |

---

## 4. How to Run

### Prerequisites
Activate the Python virtual environment:
```bash
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### Run Clean Execution (Transcript 1)
Runs the agent with all tools operational. Generates a clean reasoning trace and final architectural recommendation:
```bash
python assignment-1/run.py
```
*Outputs to console and saves `assignment-1/transcripts/transcript_clean_run.md`.*

### Run Mocked Tool Failure Mode (Transcript 2)
Injects a 503 service timeout into the latency calculator to demonstrate autonomous fault detection and recovery:
```bash
python assignment-1/run.py --fail-tool
```
*Outputs to console and saves `assignment-1/transcripts/transcript_failure_run.md`.*

### Optional: Using Live LLM Providers
Set your API key in `.env` or pass the `--provider` flag:
```bash
# Google Gemini (Free tier, recommended)
set GEMINI_API_KEY=your_key_here
python assignment-1/run.py --provider gemini

# Groq (Free tier)
set GROQ_API_KEY=your_key_here
python assignment-1/run.py --provider groq
```
*Note: If no API key is provided, the agent runs in a deterministic autonomous planner mode out of the box, ensuring zero-configuration execution from any clean clone.*

---

## 5. Transcripts
- [Transcript 1: Clean Run](transcripts/transcript_clean_run.md)
- [Transcript 2: Mocked Tool Failure Run](transcripts/transcript_failure_run.md)
