# Assignment 2: Multi-Agent Task with Review

## 1. Overview
This project implements a sequential multi-agent review pipeline using **LangGraph**. The workflow tests clean agent handoffs and objective, criteria-based peer review between two specialized agents without introducing negotiation loops.

### Task Definition
> *"Write a production-grade Python `TokenBucketRateLimiter` class implementing the Token Bucket algorithm with type annotations, docstrings, thread-safety, and edge-case validation."*

---

## 2. Agent Architecture & Workflow

```
[ START ] ➔ [ Agent A: Worker ] ➔ [ Agent B: Reviewer ] ➔ [ END ]
```

1. **Agent A (Worker)**:
   - Takes the design specification and produces a single code implementation attempt.
   - Handoffs the raw code artifact directly to the shared LangGraph state.
2. **Agent B (Reviewer)**:
   - Inspects Agent A's code against a concrete, objective 5-point evaluation rubric.
   - Determines an unequivocal verdict: **`APPROVED`** or **`REJECTED`**.
   - If rejected, itemizes the exact failing criteria and technical vulnerabilities.
   - Emits an execution report with total agent calls and token metrics.
3. **No Revision Loop Constraint**:
   - The chain executes in a single pass (Worker ➔ Reviewer ➔ End), guaranteeing deterministic completion and preventing infinite negotiation cycles.

---

## 3. Agent B's Concrete Approval Criteria

Agent B does not use vague "looks good" heuristics. It evaluates code against **five distinct, measurable criteria**:

| Criterion ID | Name | Pass Standard |
|---|---|---|
| **`C1_ALGORITHM_CORRECTNESS`** | Token Bucket Mathematical Correctness | Tokens replenished strictly via monotonic time delta: `min(capacity, current + elapsed * rate)`. Deducts tokens on successful request. |
| **`C2_THREAD_SAFETY`** | Concurrency & Mutex Synchronization | State mutations (`self.tokens`, `self.last_updated`) must be guarded by `threading.Lock` or `threading.RLock`. |
| **`C3_INPUT_VALIDATION_EDGE_CASES`** | Input Validation & Defensiveness | Defensively raises `ValueError` for non-positive `capacity`, non-positive `fill_rate`, or negative requested tokens. |
| **`C4_TYPE_HINTS_AND_DOCUMENTATION`** | Type Annotations & PEP 257 Docstrings | Complete PEP 484 type hints on all method signatures and comprehensive docstrings explaining arguments and returns. |
| **`C5_INTERFACE_ERGONOMICS_TESTABILITY`** | Interface Ergonomics & Testability | Clean boolean consumption API (`allow_request()`) and support for dependency-injecting a monotonic clock source for testing. |

---

## 4. How to Run

### Run Approval Flow (Transcript 1)
Demonstrates a production-ready code submission from Agent A that passes all 5 criteria and receives an `APPROVED` verdict:
```bash
python assignment-2/run.py --mode approved
```
*Outputs to console and saves `assignment-2/transcripts/transcript_approved.md`.*

### Run Rejection Flow (Transcript 2)
Demonstrates Agent A producing a weaker attempt (missing thread locks, missing docstrings, and unvalidated edge cases) which Agent B catches and issues a `REJECTED` verdict with itemized reasons:
```bash
python assignment-2/run.py --mode rejected
```
*Outputs to console and saves `assignment-2/transcripts/transcript_rejected.md`.*

### Optional: Using Live LLM Providers
```bash
# Google Gemini (Free tier, recommended)
set GEMINI_API_KEY=your_key_here
python assignment-2/run.py --provider gemini

# Groq (Free tier)
set GROQ_API_KEY=your_key_here
python assignment-2/run.py --provider groq
```

---

## 5. Deliverable Transcripts
- [Transcript 1: Approved Run](transcripts/transcript_approved.md)
- [Transcript 2: Rejected Run](transcripts/transcript_rejected.md)
