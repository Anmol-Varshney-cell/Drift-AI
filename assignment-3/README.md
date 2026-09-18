# Assignment 3: Resumable Agent with Basic Self-Check

## 1. Overview
This project implements a long-running, fault-tolerant batch processing agent using **LangGraph's built-in state checkpointing (`SqliteSaver`)**. The agent processes items one at a time, persists progress to disk after each item, seamlessly resumes if interrupted, and executes a terminal self-check step to catch defective or empty outputs.

### Task Definition
> *"Process 4 technical incident postmortem reports (`INC-101` through `INC-104`) sequentially, extracting Incident Title, Root Cause, Downtime Duration, and Remediation Actions into structured summaries."*

---

## 2. Checkpointing Architecture & State Design

In strict adherence to the assignment requirements (*"use LangGraph's built-in state/checkpointing rather than hand-rolling your own"*), this implementation utilizes **`langgraph.checkpoint.sqlite.SqliteSaver`** writing to a local SQLite database (`state_checkpoint.db`).

### Saved State Schema
The persisted state is kept clean, human-readable, and minimal:
```json
{
  "current_index": 2,
  "completed_ids": ["INC-101", "INC-102"],
  "status": "interrupted",
  "total_llm_calls": 2,
  "processed_count": 2,
  "results_summary": {
    "INC-101": {
      "title": "Auth Service JWT Secret Rotation Outage",
      "summary_length": 237
    },
    "INC-102": {
      "title": "Postgres Connection Pool Exhaustion on Payments API",
      "summary_length": 263
    }
  }
}
```

### Resumption Mechanics
1. Each run is bound to a consistent session `thread_id` (`incident_batch_thread_001`).
2. When the agent starts or restarts, LangGraph loads the latest checkpoint from SQLite.
3. If an item's ID is already present in `completed_ids`, the node logs `[RESUME SKIP]` and skips re-processing it, ensuring zero redundant LLM calls or duplicate work.
4. When all items reach completion, the workflow transitions to the `self_check` node.

---

## 3. Terminal Self-Check Step
After all 4 items are processed, the agent enters a verification node (`self_check`):
- Re-reads all processed results from state.
- Asserts that every record exists, is non-empty, and contains valid summary fields.
- Flags any empty string or corrupted schema and reports a `CHECK_PASSED` or `CHECK_FAILED` verdict.

---

## 4. How to Run

### Automated Stop & Resume Demo (Transcript 1)
Executes the full stop-and-resume lifecycle:
1. Runs initial batch with `--stop-at 2` (processes items 1 & 2, then interrupts before item 3).
2. Re-runs with the same `thread_id` (skips items 1 & 2 from checkpoint, processes items 3 & 4, and runs self-check).
```bash
python assignment-3/run.py --demo-stop-resume
```
*Outputs to console and saves `assignment-3/transcripts/transcript_stop_resume.md`.*

### Automated Self-Check Defect Detection Demo (Transcript 2)
Deliberately corrupts/blanks item `INC-103` during extraction to verify that the self-check node catches and flags the defect:
```bash
python assignment-3/run.py --demo-self-check
```
*Outputs to console and saves `assignment-3/transcripts/transcript_self_check.md`.*

### Manual Step-by-Step CLI Commands
You can also trigger individual phases manually:
```bash
# 1. Start clean and stop at index 2 (before INC-103)
python assignment-3/run.py --clear-db --stop-at 2

# 2. Resume from the checkpoint and finish the batch
python assignment-3/run.py

# 3. Test corruption on a specific item ID
python assignment-3/run.py --clear-db --corrupt-item INC-103
```

---

## 5. Deliverable Transcripts
- [Transcript 1: Stop Partway & Resume Log](transcripts/transcript_stop_resume.md)
- [Transcript 2: Self-Check Catching Corrupted Item Log](transcripts/transcript_self_check.md)
