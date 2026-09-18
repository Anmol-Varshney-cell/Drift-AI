"""
CLI Runner for Assignment 3: Resumable Agent with Basic Self-Check.
Demonstrates:
1. Stop partway (e.g. at item 2) -> Resume from disk checkpoint -> Skips already completed items -> Completes.
2. Self-check step catching a deliberately corrupted / empty result.
Reports total LLM calls.
"""

import os
import sys
import argparse
import json
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.llm import get_llm
from resumable_agent import create_resumable_graph
from dataset import INCIDENT_REPORTS

DB_FILE = os.path.join(os.path.dirname(__file__), "state_checkpoint.db")
THREAD_ID = "incident_batch_thread_001"

def format_state_readable(state: dict) -> str:
    """Formats saved state into a clear, human-readable JSON block."""
    clean = {
        "current_index": state.get("current_index"),
        "completed_ids": state.get("completed_ids", []),
        "status": state.get("status"),
        "total_llm_calls": state.get("total_llm_calls"),
        "processed_count": len(state.get("results", {})),
        "results_summary": {k: {"title": v["title"], "summary_length": len(v["summary_text"])} for k, v in state.get("results", {}).items()}
    }
    return json.dumps(clean, indent=2)


def run_assignment_3(
    action: str = "full",
    stop_at: int = None,
    corrupt_item: str = None,
    provider: str = None,
    clear_db: bool = False
):
    if clear_db and os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
            print(f"🧹 Cleared old checkpoint database: {DB_FILE}")
        except Exception:
            pass

    print("=" * 80)
    print(f"🚀 Running Assignment 3: Resumable Incident Summarizer [Action: {action.upper()}]")
    print(f"📁 Checkpoint Database: {DB_FILE}")
    print(f"🧵 Session Thread ID: {THREAD_ID}")
    print("=" * 80)

    llm = get_llm(provider=provider)
    graph = create_resumable_graph(db_path=DB_FILE, llm=llm)
    config = {"configurable": {"thread_id": THREAD_ID}}

    # Check if existing state exists in checkpoint
    existing_state = graph.get_state(config)
    
    if existing_state and existing_state.values:
        print(f"🔄 Resuming from existing checkpoint found on disk!")
        print("💾 Current Persisted State:")
        print(format_state_readable(existing_state.values))
        print("-" * 80)
        
        # Merge resumed state
        current_state = dict(existing_state.values)
        if corrupt_item:
            current_state["corrupt_target_id"] = corrupt_item
        if stop_at is not None:
            current_state["stop_at_index"] = stop_at
        else:
            current_state["stop_at_index"] = None
    else:
        print("🆕 No prior checkpoint found. Initializing brand new run state.")
        current_state = {
            "current_index": 0,
            "completed_ids": [],
            "results": {},
            "check_records": [],
            "status": "in_progress",
            "stop_at_index": stop_at,
            "corrupt_target_id": corrupt_item,
            "total_llm_calls": 0,
            "log_messages": []
        }

    # Execute graph with checkpointer
    final_output = graph.invoke(current_state, config=config)

    print("\n" + "=" * 80)
    print("🏁 Step Execution Completed!")
    print(f"Status: {final_output['status']}")
    print(f"Completed Items: {final_output['completed_ids']}")
    print(f"Total LLM Calls: {final_output['total_llm_calls']}")
    print("=" * 80)

    print("\n💾 Persisted State in Database:")
    print(format_state_readable(final_output))
    return final_output

def generate_stop_resume_transcript():
    """Executes the two-step run -> stop partway -> re-run -> completes flow and writes transcript."""
    transcripts_dir = os.path.join(os.path.dirname(__file__), "transcripts")
    os.makedirs(transcripts_dir, exist_ok=True)
    out_file = os.path.join(transcripts_dir, "transcript_stop_resume.md")

    log_lines = []
    log_lines.append("# Assignment 3 — Resumable Agent Execution Transcript (Stop & Resume)\n")
    log_lines.append(f"**Timestamp**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    log_lines.append(f"**Task**: Process 4 incident postmortem reports sequentially with persistent LangGraph checkpointing.\n")

    log_lines.append("## Phase 1: Initial Run Interrupted Partway (`--stop-at 2`)\n")
    log_lines.append("Simulates a process interruption (e.g. Ctrl+C or worker preemption) after processing 2 items.\n")
    log_lines.append("```text")
    
    # Run Phase 1
    state1 = run_assignment_3(action="phase1_interrupt", stop_at=2, clear_db=True)
    for msg in state1.get("log_messages", []):
        log_lines.append(msg)
    log_lines.append("```\n")
    
    log_lines.append("### Saved State at Interruption Point\n")
    log_lines.append("```json\n" + format_state_readable(state1) + "\n```\n")

    log_lines.append("## Phase 2: Resuming from Checkpoint (`--resume`)\n")
    log_lines.append("Re-running with the same thread_id. The agent detects existing state, skips INC-101 and INC-102, and processes the remaining items.\n")
    log_lines.append("```text")

    # Run Phase 2
    state2 = run_assignment_3(action="phase2_resume", stop_at=None, clear_db=False)
    for msg in state2.get("log_messages", []):
        log_lines.append(msg)
    log_lines.append("```\n")

    log_lines.append("### Final Persisted State After Resumption\n")
    log_lines.append("```json\n" + format_state_readable(state2) + "\n```\n")

    log_lines.append("## Final Summary\n")
    log_lines.append(f"- **Total Items In Batch**: {len(INCIDENT_REPORTS)}")
    log_lines.append(f"- **Items Successfully Processed**: {len(state2.get('completed_ids', []))}")
    log_lines.append(f"- **Skipped Completed Items on Resume**: INC-101, INC-102 (Zero redundant work performed)")
    log_lines.append(f"- **Total LLM Calls Across Both Sessions**: {state2.get('total_llm_calls')}")
    log_lines.append(f"- **Self-Check Status**: `{state2.get('status')}`")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))
    print(f"\n✅ Transcript 1 saved to: {out_file}")


def generate_self_check_transcript():
    """Executes run with a deliberately corrupted item and writes transcript."""
    transcripts_dir = os.path.join(os.path.dirname(__file__), "transcripts")
    os.makedirs(transcripts_dir, exist_ok=True)
    out_file = os.path.join(transcripts_dir, "transcript_self_check.md")

    log_lines = []
    log_lines.append("# Assignment 3 — Self-Check Validation Transcript (Catching Defect)\n")
    log_lines.append(f"**Timestamp**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    log_lines.append(f"**Task**: Run batch processing with deliberate chaos injection (`INC-103` corrupted) to verify self-check detection.\n")
    log_lines.append("```text")

    state = run_assignment_3(action="chaos_injection", corrupt_item="INC-103", clear_db=True)
    for msg in state.get("log_messages", []):
        log_lines.append(msg)
    log_lines.append("```\n")

    log_lines.append("## Self-Check Validation Results\n")
    for r in state.get("check_records", []):
        mark = "✅ PASS" if r["passed"] else "❌ FAIL"
        log_lines.append(f"- **Item {r['item_id']}**: {mark}")
        if r.get("issue"):
            log_lines.append(f"  *Identified Defect*: `{r['issue']}`")

    log_lines.append(f"\n- **Final Self-Check Verdict**: `{state.get('status')}`")
    log_lines.append(f"- **Total LLM Calls**: {state.get('total_llm_calls')}")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))
    print(f"\n✅ Transcript 2 saved to: {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Assignment 3 Resumable Agent")
    parser.add_argument("--stop-at", type=int, default=None, help="Stop/interrupt before processing item index N (0-indexed)")
    parser.add_argument("--corrupt-item", type=str, default=None, help="ID of item to deliberately corrupt/blank for self-check testing (e.g. INC-103)")
    parser.add_argument("--clear-db", action="store_true", help="Clear sqlite checkpoint database before running")
    parser.add_argument("--demo-stop-resume", action="store_true", help="Run full automated stop-and-resume workflow and generate Transcript 1")
    parser.add_argument("--demo-self-check", action="store_true", help="Run self-check flaw detection workflow and generate Transcript 2")
    parser.add_argument("--provider", type=str, default=None, choices=["gemini", "groq", "openai", "mock"], help="LLM Provider")

    args = parser.parse_args()

    if args.demo_stop_resume:
        generate_stop_resume_transcript()
    elif args.demo_self_check:
        generate_self_check_transcript()
    else:
        run_assignment_3(
            action="manual",
            stop_at=args.stop_at,
            corrupt_item=args.corrupt_item,
            provider=args.provider,
            clear_db=args.clear_db
        )
