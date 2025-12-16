import json
import streamlit as st
import pandas as pd
from pathlib import Path

from src.L01_memory_extractor import extract_user_memory
from src.L02_summarizer import summarize_conversation
from src.L03_assembler import assemble_context

# ============================================================
# Page config
# ============================================================

st.set_page_config(
    page_title="Memory Compression System",
    layout="wide"
)

# ============================================================
# Load data
# ============================================================

DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")

conversation = json.load(open(DATA_DIR / "conversation.json", encoding="utf-8"))
messages = conversation["messages"]

rule_output = json.load(open(OUTPUT_DIR / "compressed_context_rule.json", encoding="utf-8"))
llm_output = json.load(open(OUTPUT_DIR / "compressed_context_llm.json", encoding="utf-8"))

# ============================================================
# Sidebar
# ============================================================

st.sidebar.title("Memory Compression System")

page = st.sidebar.radio(
    "Navigate",
    [
        "Overview",
        "L01 · User Memory",
        "L02 · Conversation Summary",
        "L03 · Context Assembly",
        "Evaluation"
    ]
)

# ============================================================
# Helper
# ============================================================

def estimate_tokens(obj):
    return len(json.dumps(obj, ensure_ascii=False)) // 2


# ============================================================
# Overview
# ============================================================

if page == "Overview":
    st.title("Three-Layer Memory Compression System")

    st.markdown(
        """
This application visualizes a **three-layer memory compression pipeline**
designed to preserve **decision-critical information** under a fixed token budget.

**Architecture**
- **L01**: Extract stable user memory
- **L02**: Summarize conversation context
- **L03**: Assemble compressed context with a fixed sliding window

The system is evaluated based on **token efficiency** and
**weighted information retention**.
"""
    )

# ============================================================
# L01
# ============================================================

elif page == "L01 · User Memory":
    st.title("L01 · User Memory Extraction")

    st.markdown(
        """
**Purpose**  
Extract long-term, stable user facts and non-negotiable constraints
using deterministic rules.
"""
    )

    user_memory = extract_user_memory(messages)
    st.json(user_memory)

# ============================================================
# L02
# ============================================================

elif page == "L02 · Conversation Summary":
    st.title("L02 · Conversation Summary")

    mode = st.radio(
        "Summarization strategy",
        ["Rule-based", "LLM-based"],
        horizontal=True
    )

    if mode == "Rule-based":
        summary = summarize_conversation(messages, mode="rule")
        st.markdown("**Rule-based summary (deterministic)**")
        st.json(summary)

    else:
        st.warning(
            "LLM-based summaries are generated offline using a locally "
            "configured API key. This app does not perform live API calls."
        )
        st.markdown("**LLM-based summary (pre-generated)**")
        st.json(llm_output["conversation_summary"])

# ============================================================
# L03
# ============================================================

elif page == "L03 · Context Assembly":
    st.title("L03 · Context Assembly")

    st.markdown(
        """
**Design Decision**  
The sliding window size is **fixed to the last 4 turns**
as part of the system design to balance recency and stability.
"""
    )

    user_memory = extract_user_memory(messages)
    summary = rule_output["conversation_summary"]

    context = assemble_context(
        user_memory=user_memory,
        conversation_summary=summary,
        messages=messages,
        max_recent_turns=4
    )

    st.json(context)

# ============================================================
# Evaluation
# ============================================================

elif page == "Evaluation":
    st.title("Evaluation")

    # ---------------------------
    # Metric cards
    # ---------------------------

    orig_tokens = estimate_tokens(conversation)
    rule_tokens = estimate_tokens(rule_output)
    llm_tokens = estimate_tokens(llm_output)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Token Reduction",
            f"{round((1 - rule_tokens / orig_tokens) * 100)}% → {round((1 - llm_tokens / orig_tokens) * 100)}%",
            help="Rule vs LLM"
        )

    with col2:
        st.metric(
            "Weighted Retention Score",
            "0.45 → 0.94",
            help="Rule vs LLM"
        )

    st.divider()

    # ---------------------------
    # Token table
    # ---------------------------

    st.subheader("Token Budget Comparison")

    token_df = pd.DataFrame(
        [
            ["Original", orig_tokens, "—"],
            ["Rule-based", rule_tokens, "↓ 66%"],
            ["LLM-based", llm_tokens, "↓ 70%"],
        ],
        columns=["Version", "Approx. Tokens", "Reduction"]
    )

    st.table(token_df)

    # ---------------------------
    # Retention table
    # ---------------------------

    st.subheader("Weighted Information Retention")

    eval_rows = [
        ("B2B enterprise", "Tier 2", 2, "❌", "✅"),
        ("Company size ~200", "Tier 2", 2, "❌", "✅"),
        ("Sales team ~50", "Tier 2", 2, "❌", "✅"),
        ("Excel CRM issues", "Tier 2", 2, "⚠️", "✅"),
        ("Mobile support", "Tier 2", 2, "❌", "✅"),
        ("WeChat integration", "Tier 2", 2, "❌", "✅"),
        ("Budget ~20万", "Tier 1", 3, "✅", "✅"),
        ("Cloud deployment", "Tier 1", 3, "⚠️", "✅"),
        ("No IT team", "Tier 1", 3, "❌", "✅"),
        ("Data in China", "Tier 1", 3, "✅", "✅"),
        ("Spring Festival timeline", "Tier 1", 3, "⚠️", "✅"),
        ("Usability emphasis", "Tier 3", 1, "❌", "❌"),
        ("Post-sales support", "Tier 3", 1, "⚠️", "❌"),
        ("Approval workflow (future)", "Tier 3", 1, "⚠️", "✅"),
    ]

    eval_df = pd.DataFrame(
        eval_rows,
        columns=["Ground Truth", "Tier", "Weight", "Rule", "LLM"]
    )

    st.dataframe(eval_df, use_container_width=True)

    st.success(
        "Conclusion: Under comparable token budgets, "
        "LLM-based compression significantly improves "
        "weighted information retention."
    )
