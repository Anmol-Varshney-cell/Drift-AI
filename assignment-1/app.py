"""
Streamlit Web Application for Assignment 1: Tool-Using Research Agent (LangGraph).
Deployable directly via Streamlit Cloud or locally via:
    streamlit run assignment-1/app.py
"""

import os
import sys
import json
import streamlit as st

# Setup import paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.llm import get_llm
from agent import create_research_graph
from tools import set_simulate_tool_failure

st.set_page_config(
    page_title="Assignment 1: Research Agent",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 Assignment 1: Tool-Using Research Agent")
st.caption("Autonomous dynamic planning, multi-tool investigation, budget enforcement, and graceful fault recovery built with **LangGraph**.")

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Agent Configuration")
    
    provider_choice = st.selectbox(
        "LLM Provider",
        ["Deterministic Planner (Offline / Free)", "Google Gemini", "Groq", "OpenAI"],
        index=0,
        help="Select model provider. The deterministic planner runs instantly without API keys."
    )
    
    api_key = None
    if provider_choice == "Google Gemini":
        api_key = st.text_input("GEMINI_API_KEY", type="password", value=os.getenv("GEMINI_API_KEY", ""))
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
    elif provider_choice == "Groq":
        api_key = st.text_input("GROQ_API_KEY", type="password", value=os.getenv("GROQ_API_KEY", ""))
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
    elif provider_choice == "OpenAI":
        api_key = st.text_input("OPENAI_API_KEY", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

    st.markdown("---")
    st.subheader("🧪 Chaos & Failure Testing")
    fail_tool = st.toggle(
        "Simulate Tool 503 Timeout",
        value=False,
        help="Simulates an upstream outage / timeout on the latency calculator tool to test autonomous adaptation."
    )

    if fail_tool:
        st.warning("⚠️ 503 Timeout Injected into `latency_sla_calculator`. The agent will detect the failure and adapt its strategy.")
    else:
        st.info("✅ All tools operating normally.")

    max_calls = st.slider("Tool Call Budget Limit", min_value=3, max_value=8, value=6, help="Hard ceiling on tool calls per run.")

# Main Question Input
DEFAULT_Q = (
    "Compare two approaches to API caching for a read-heavy system "
    "(Redis cache-aside vs. Cloudflare CDN edge caching) and recommend an architecture "
    "for 10k req/sec with dynamic user-specific data."
)

question = st.text_area("Target Research Question:", value=DEFAULT_Q, height=100)

run_button = st.button("🚀 Run Research Agent", type="primary", use_container_width=True)

if run_button:
    # Configure simulation flag
    set_simulate_tool_failure(fail_tool)
    
    # Initialize LLM
    provider_map = {
        "Google Gemini": "gemini",
        "Groq": "groq",
        "OpenAI": "openai",
        "Deterministic Planner (Offline / Free)": "mock"
    }
    llm = get_llm(provider=provider_map[provider_choice])

    with st.spinner("🤖 Agent is planning and investigating via LangGraph..."):
        graph = create_research_graph(llm=llm)
        initial_state = {
            "question": question,
            "messages": [],
            "tool_call_count": 0,
            "max_tool_calls": max_calls,
            "collected_evidence": {},
            "reasoning_trace": [],
            "next_action": None,
            "status": "planning",
            "final_answer": None
        }
        final_state = graph.invoke(initial_state)

    # Metrics Bar
    col1, col2, col3 = st.columns(3)
    col1.metric("Tool Calls Used", f"{final_state['tool_call_count']} / {final_state['max_tool_calls']}")
    col2.metric("Execution Status", final_state["status"].upper())
    col3.metric("Failure Mode Active", "YES (503 Injected)" if fail_tool else "NO (Clean)")

    st.markdown("---")

    # Final Output
    st.subheader("📝 Final Synthesized Recommendation")
    st.markdown(final_state.get("final_answer", "No final answer generated."))

    st.markdown("---")

    # Step-by-Step Reasoning Trace
    st.subheader("🔍 Step-by-Step Reasoning Trace")
    st.caption("Inspect how the agent dynamically planned its steps, evaluated observations, and handled errors.")

    for item in final_state["reasoning_trace"]:
        step = item.get("step", "-")
        if "decision" in item:
            with st.expander(f"Step {step}: Decision ➔ {item['decision']}", expanded=True):
                if "thought" in item:
                    st.markdown(f"**🧠 Thought:** {item['thought']}")
                st.markdown(f"**🎯 Decision:** {item['decision']}")
                if "why" in item:
                    st.markdown(f"**💡 Technical Rationale (Why):** {item['why']}")
                if "action" in item:
                    st.markdown(f"**⚡ Planned Action:** `{item['action']}`")
        elif "tool_called" in item:
            with st.expander(f"Step {step}: Tool Execution ➔ `{item['tool_called']}` (Call #{item.get('tool_call_number')})", expanded=False):
                st.markdown(f"**Parameters:** `{json.dumps(item.get('parameters', {}))}`")
                obs = item.get("observation")
                if isinstance(obs, dict) and "error" in obs:
                    st.error(f"Observation (Tool Error):\n```json\n{json.dumps(obs, indent=2)}\n```")
                else:
                    st.json(obs)

    # Download transcript
    transcript_md = f"# Execution Transcript\n\nQuestion: {question}\n\nStatus: {final_state['status']}\n\nFinal Recommendation:\n{final_state.get('final_answer')}"
    st.download_button(
        label="📥 Download Transcript as Markdown",
        data=transcript_md,
        file_name="assignment_1_transcript.md",
        mime="text/markdown"
    )
