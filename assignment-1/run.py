"""
CLI Runner for Assignment 1: Tool-Using Research Agent.
Supports:
1. Clean execution (no tool failure) -> generates transcript 1
2. Failure injection execution (mocked timeout/error on tool) -> generates transcript 2
3. Live LLM execution (Google Gemini / Groq / OpenAI) or deterministic simulation mode.
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

# Setup imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.llm import get_llm
from agent import create_research_graph
from tools import set_simulate_tool_failure

DEFAULT_QUESTION = (
    "Compare two approaches to API caching for a read-heavy system "
    "(Redis cache-aside vs. Cloudflare CDN edge caching) and recommend an architecture "
    "for 10k req/sec with dynamic user-specific data."
)

def format_transcript_markdown(run_type: str, question: str, final_state: dict) -> str:
    lines = []
    lines.append(f"# Assignment 1 — Research Agent Execution Transcript ({run_type})\n")
    lines.append(f"**Timestamp**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append(f"**Target Question**: *\"{question}\"*")
    lines.append(f"**Total Tool Calls Used**: {final_state['tool_call_count']} / {final_state['max_tool_calls']}")
    lines.append(f"**Execution Status**: `{final_state['status']}`\n")
    lines.append("## Step-by-Step Reasoning Trace\n")

    for item in final_state["reasoning_trace"]:
        step = item.get("step", "-")
        lines.append(f"### Step {step}")
        if "thought" in item:
            lines.append(f"- **Thought**: {item['thought']}")
        if "decision" in item:
            lines.append(f"- **Decision**: {item['decision']}")
        if "why" in item:
            lines.append(f"- **Why**: {item['why']}")
        if "action" in item:
            lines.append(f"- **Action**: {item['action']}")
        if "tool_called" in item:
            lines.append(f"- **Tool Called**: `{item['tool_called']}` (Call #{item.get('tool_call_number', 1)})")
            lines.append(f"- **Parameters**: `{json.dumps(item.get('parameters', {}))}`")
        if "observation" in item:
            lines.append(f"- **Observation**:\n```json\n{json.dumps(item['observation'], indent=2) if isinstance(item['observation'], (dict, list)) else item['observation']}\n```")
        if "result" in item:
            lines.append(f"- **Result**: {item['result']}")
        lines.append("")

    lines.append("## Final Synthesized Recommendation\n")
    lines.append(final_state.get("final_answer", "No final answer generated."))
    return "\n".join(lines)


def run_agent(fail_tool: bool = False, provider: str = None, save_transcript: bool = True):
    print("=" * 80)
    mode_name = "Mocked Tool Failure Mode" if fail_tool else "Clean Execution Mode"
    print(f"🚀 Starting Assignment 1 Research Agent [{mode_name}]")
    print(f"❓ Question: {DEFAULT_QUESTION}")
    print("=" * 80)

    # Set tool failure state
    set_simulate_tool_failure(fail_tool)

    # Initialize LLM (if API key available or requested)
    llm = get_llm(provider=provider)
    if llm:
        print(f"🤖 Connected to LLM provider: {type(llm).__name__}")
    else:
        print("💡 No external API key detected; running in deterministic autonomous planner mode.")

    # Build LangGraph graph
    graph = create_research_graph(llm=llm)

    initial_state = {
        "question": DEFAULT_QUESTION,
        "messages": [],
        "tool_call_count": 0,
        "max_tool_calls": 6,
        "collected_evidence": {},
        "reasoning_trace": [],
        "next_action": None,
        "status": "planning",
        "final_answer": None
    }

    # Execute graph
    final_state = graph.invoke(initial_state)

    print("\n" + "=" * 80)
    print("🏁 Execution Completed!")
    print(f"Total Tool Calls: {final_state['tool_call_count']} / {final_state['max_tool_calls']}")
    print(f"Final Status: {final_state['status']}")
    print("=" * 80)

    # Display reasoning trace summary
    print("\n📋 Reasoning Trace Summary:")
    for trace in final_state["reasoning_trace"]:
        if "decision" in trace:
            print(f"  [Step {trace.get('step')}] Decision: {trace['decision']}")
            print(f"         Why: {trace.get('why', '')[:100]}...")
        elif "tool_called" in trace:
            print(f"  [Step {trace.get('step')}] Tool Call #{trace['tool_call_number']}: {trace['tool_called']}")

    print("\n" + "=" * 80)
    print("📝 Final Synthesized Output:")
    print("=" * 80)
    print(final_state.get("final_answer", ""))

    if save_transcript:
        os.makedirs(os.path.join(os.path.dirname(__file__), "transcripts"), exist_ok=True)
        filename = "transcript_failure_run.md" if fail_tool else "transcript_clean_run.md"
        filepath = os.path.join(os.path.dirname(__file__), "transcripts", filename)
        markdown_content = format_transcript_markdown(mode_name, DEFAULT_QUESTION, final_state)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"\n✅ Transcript saved to: {filepath}")

    return final_state

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Assignment 1 Research Agent")
    parser.add_argument("--fail-tool", action="store_true", help="Simulate a tool failure (e.g. 503 timeout on latency calculator)")
    parser.add_argument("--provider", type=str, default=None, choices=["gemini", "groq", "openai", "mock"], help="LLM Provider to use")
    parser.add_argument("--no-save", action="store_true", help="Do not save transcript to file")

    args = parser.parse_args()
    run_agent(fail_tool=args.fail_tool, provider=args.provider, save_transcript=not args.no_save)
