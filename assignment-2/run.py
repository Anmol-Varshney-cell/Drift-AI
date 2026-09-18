"""
CLI Runner for Assignment 2: Multi-Agent Task with Review.
Generates:
1. Transcript 1: Approved Run (Worker produces high quality code -> Reviewer approves)
2. Transcript 2: Rejected Run (Worker produces flawed code -> Reviewer rejects with itemized reasons)
Tracks and reports total LLM calls and token counts.
"""

import os
import sys
import argparse
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.llm import get_llm
from multi_agent import create_multi_agent_chain

TASK_DESCRIPTION = (
    "Write a production-grade Python TokenBucketRateLimiter class implementing "
    "the Token Bucket algorithm with type annotations, docstring, thread-safety, "
    "and edge-case validation."
)

def format_transcript_markdown(mode: str, state: dict) -> str:
    lines = []
    lines.append(f"# Assignment 2 — Multi-Agent Review Chain Transcript ({state['verdict']})\n")
    lines.append(f"**Timestamp**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append(f"**Task**: *\"{state['task']}\"*")
    lines.append(f"**Workflow**: Agent A (Worker) ➔ Agent B (Reviewer) ➔ END")
    lines.append(f"**Total LLM Calls**: {state['total_llm_calls']}")
    lines.append(f"**Total Tokens Used (Estimated/Reported)**: {state['total_tokens_used']}")
    lines.append(f"**Final Verdict**: `{state['verdict']}`\n")

    lines.append("## 1. Agent A (Worker) Output\n")
    lines.append("```python")
    lines.append(state["worker_code"])
    lines.append("```\n")

    lines.append("## 2. Agent B (Reviewer) Assessment\n")
    lines.append(state["reviewer_summary"])
    lines.append("\n")

    lines.append("## 3. Resource Usage Report\n")
    lines.append(f"- **Agent Invocations**: 2 agents (1 Worker call, 1 Reviewer call)")
    lines.append(f"- **Total LLM Calls**: {state['total_llm_calls']}")
    lines.append(f"- **Total Tokens Consumed**: {state['total_tokens_used']} tokens")
    lines.append(f"- **Negotiation Loops**: 0 (strict single-review compliance)")

    return "\n".join(lines)


def run_multi_agent(mode: str = "approved", provider: str = None, save_transcript: bool = True):
    print("=" * 80)
    print(f"🤖 Starting Assignment 2 Multi-Agent Chain [Mode: {mode.upper()}]")
    print(f"📋 Task: {TASK_DESCRIPTION}")
    print("=" * 80)

    llm = get_llm(provider=provider)
    if llm:
        print(f"🤖 Connected to LLM provider: {type(llm).__name__}")
    else:
        print("💡 No external API key detected; running deterministic multi-agent chain.")

    chain = create_multi_agent_chain(llm=llm)

    flow_mode = "approved_flow" if mode == "approved" else "rejected_flow"
    initial_state = {
        "task": TASK_DESCRIPTION,
        "mode": flow_mode,
        "worker_code": None,
        "verdict": None,
        "rubric_evaluation": {},
        "rejection_reasons": [],
        "reviewer_summary": None,
        "total_llm_calls": 0,
        "total_tokens_used": 0
    }

    final_state = chain.invoke(initial_state)

    print("\n" + "=" * 80)
    print("🏁 Execution Completed!")
    print(f"Agent B Final Verdict: {final_state['verdict']}")
    print(f"Total LLM Calls: {final_state['total_llm_calls']}")
    print(f"Total Tokens Used: {final_state['total_tokens_used']}")
    print("=" * 80)

    print("\n" + final_state["reviewer_summary"])

    if save_transcript:
        os.makedirs(os.path.join(os.path.dirname(__file__), "transcripts"), exist_ok=True)
        filename = "transcript_approved.md" if final_state["verdict"] == "APPROVED" else "transcript_rejected.md"
        filepath = os.path.join(os.path.dirname(__file__), "transcripts", filename)
        content = format_transcript_markdown(mode, final_state)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n✅ Transcript saved to: {filepath}")

    return final_state

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Assignment 2 Multi-Agent Review Chain")
    parser.add_argument("--mode", choices=["approved", "rejected"], default="approved", help="Simulation mode (approved or rejected)")
    parser.add_argument("--provider", type=str, default=None, choices=["gemini", "groq", "openai", "mock"], help="LLM Provider")
    parser.add_argument("--no-save", action="store_true", help="Do not save transcript to file")

    args = parser.parse_args()
    run_multi_agent(mode=args.mode, provider=args.provider, save_transcript=not args.no_save)
