"""
Main Streamlit Multi-Assignment Portal.
Interactive demonstration suite for Assignment 1 & Assignment 2 built with LangGraph.
Deployable as the main file path on Streamlit Community Cloud:
    app.py
Or run locally:
    streamlit run app.py
"""

import os
import sys
import json
import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="Junior AI Engineer Take-Home Dashboard",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Autonomous Agent Products — LangGraph Dashboard")
st.markdown("Interactive demonstration suite for **Assignment 1** & **Assignment 2** built using **LangGraph**.")

tab1, tab2 = st.tabs([
    "🔬 Assignment 1: Research Agent",
    "👥 Assignment 2: Multi-Agent Review"
])

# ---------------------------------------------------------
# TAB 1: ASSIGNMENT 1
# ---------------------------------------------------------
with tab1:
    from shared.llm import get_llm
    sys.path.append(os.path.join(os.path.dirname(__file__), "assignment-1"))
    import agent as a1_agent
    import tools as a1_tools

    st.subheader("Assignment 1: Tool-Using Research Agent")
    st.caption("Autonomous planning, budget tracking (<= 6 calls), and 503 timeout fault adaptation.")

    col1, col2 = st.columns([3, 1])
    with col1:
        default_q = (
            "Compare two approaches to API caching for a read-heavy system "
            "(Redis cache-aside vs. Cloudflare CDN edge caching) and recommend an architecture "
            "for 10k req/sec with dynamic user-specific data."
        )
        q1 = st.text_area("Research Question", value=default_q, height=90, key="a1_q")
    with col2:
        fail_tool_a1 = st.toggle("Inject 503 Tool Timeout", value=False, help="Simulates an outage on latency_sla_calculator")
        budget_a1 = st.slider("Max Calls Budget", 3, 8, 6, key="a1_budget")

    if st.button("🚀 Run Assignment 1 Agent", type="primary", key="btn_a1"):
        a1_tools.set_simulate_tool_failure(fail_tool_a1)
        graph1 = a1_agent.create_research_graph()

        with st.spinner("Agent planning and executing research loop..."):
            res1 = graph1.invoke({
                "question": q1,
                "messages": [],
                "tool_call_count": 0,
                "max_tool_calls": budget_a1,
                "collected_evidence": {},
                "reasoning_trace": [],
                "next_action": None,
                "status": "planning",
                "final_answer": None
            })

        m1, m2, m3 = st.columns(3)
        m1.metric("Tool Calls Used", f"{res1['tool_call_count']} / {res1['max_tool_calls']}")
        m2.metric("Status", res1["status"].upper())
        m3.metric("Failure Injected", "YES (503 Timeout)" if fail_tool_a1 else "NO (Clean)")

        st.subheader("📝 Synthesized Recommendation")
        st.markdown(res1.get("final_answer", ""))

        st.subheader("📋 Step-by-Step Reasoning Trace")
        for item in res1["reasoning_trace"]:
            step = item.get("step", "-")
            if "decision" in item:
                with st.expander(f"Step {step}: Decision ➔ {item['decision']}", expanded=True):
                    if "thought" in item:
                        st.markdown(f"**🧠 Thought:** {item['thought']}")
                    st.markdown(f"**🎯 Decision:** {item['decision']}")
                    if "why" in item:
                        st.markdown(f"**💡 Why:** {item['why']}")
            elif "tool_called" in item:
                with st.expander(f"Step {step}: Tool Called ➔ `{item['tool_called']}` (Call #{item.get('tool_call_number')})"):
                    st.json(item.get("observation", {}))

# ---------------------------------------------------------
# TAB 2: ASSIGNMENT 2
# ---------------------------------------------------------
with tab2:
    sys.path.append(os.path.join(os.path.dirname(__file__), "assignment-2"))
    import multi_agent as a2_ma

    st.subheader("Assignment 2: Multi-Agent Task with Review")
    st.caption("Worker Agent ➔ Reviewer Agent pipeline evaluated against 5 concrete rubric criteria (no revision loop).")

    a2_mode = st.radio(
        "Select Worker Quality Mode:",
        ["Approved Flow (High Quality Code)", "Rejected Flow (Flawed Code with Missing Locks & Validation)"],
        index=0,
        horizontal=True
    )

    if st.button("🚀 Run Multi-Agent Review Chain", type="primary", key="btn_a2"):
        flow = "approved_flow" if "Approved" in a2_mode else "rejected_flow"
        chain2 = a2_ma.create_multi_agent_chain()
        
        with st.spinner("Agent A drafting code -> Agent B evaluating rubric..."):
            res2 = chain2.invoke({
                "task": "Write a production-grade Python TokenBucketRateLimiter class with locks, docstrings, and validation.",
                "mode": flow,
                "worker_code": None,
                "verdict": None,
                "rubric_evaluation": {},
                "rejection_reasons": [],
                "reviewer_summary": None,
                "total_llm_calls": 0,
                "total_tokens_used": 0
            })

        colA, colB, colC = st.columns(3)
        verdict = res2["verdict"]
        colA.metric("Agent B Verdict", verdict)
        colB.metric("Total LLM Calls", res2["total_llm_calls"])
        colC.metric("Total Tokens", res2["total_tokens_used"])

        st.subheader("Agent B (Reviewer) Verdict & Matrix")
        st.markdown(res2["reviewer_summary"])

        with st.expander("View Agent A (Worker) Code Submission", expanded=False):
            st.code(res2["worker_code"], language="python")
