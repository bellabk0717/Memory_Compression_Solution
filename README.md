# Memory Compression with Layered Architecture

> ⚠️ **Project Scope Notice**  
> This project is intentionally designed as a **foundational and exploratory implementation**.  
>  
> Its primary goal is to demonstrate **how to reason about memory compression under context constraints**,  
> including problem decomposition, architectural trade-offs, and evaluation design —  
> **not** to deliver a production-ready system.

---

## 🔍 Overview 

This project implements a **layered memory compression system** for LLMs,
designed to compress multi-turn conversations under strict token limits
while preserving **decision-critical information**.

Conversation memory is decomposed into three explicit layers:
**L01 (stable user facts)**, **L02 (semantic conversation summary)**,
and **L03 (recent context window)**, which are assembled into the final context.

The system focuses on **in-context memory compression**:
❌ no RAG, ❌ no vector database, ❌ no retrieval.

LLM usage is isolated to a single layer (L02) and executed **offline**.
Compression quality is evaluated via **token reduction** and
**weighted information retention**, and the full pipeline is visualized using **Streamlit**.(https://memorycompressionsolution-2uz7ypsadltwtpu5fqhxvo.streamlit.app/)

---

## 📑 Table of Contents

- [Problem & Requirements](#problem--requirements)
- [Design Goals](#design-goals)
- [Assumptions & Scope](#assumptions--scope)
- [Solution Overview: Layered Memory Compression](#solution-overview-layered-memory-compression)
- [Compression Pipeline](#compression-pipeline)
- [Evaluation Methodology](#evaluation-methodology)
- [Final Conclusion](#final-conclusion)
- [Streamlit Visualization](#streamlit-visualization)
- [Limitations & Future Work](#limitations--future-work)

---

## ❓1. Problem & Requirements

Large language models operate under strict context length limits, while real-world conversations —  
especially in enterprise and decision-making scenarios — often span many turns and contain information of **uneven importance**.

The goal of this project is to:

> **Compress a multi-turn conversation into a bounded token budget while preserving decision-critical information.**

Given a full conversation and a target token constraint, the system outputs a compressed context that can still support **correct understanding and downstream reasoning**.

The core challenge is **not compression itself**, but deciding **what information should be retained under context constraints**.

---

## 📌2. Design Goals

This project is guided by the following design principles:

- Preserve **key facts, constraints, and user intent** under a strict token budget
- Make the compression process **explicit, structured, and controllable**
- Produce outputs that are **verifiable** against known key information
- Favor **engineering clarity and robustness** over opaque or complex techniques

Rather than maximizing textual similarity, the system prioritizes **decision relevance**.

---

## ✂️3. Assumptions & Scope

To keep the system interpretable and focused, the following assumptions are made:

- The conversation is **task-oriented**, with identifiable goals and constraints
- Not all dialogue turns are equally important for decision-making
- The system does **not** rely on retrieval-augmented generation (RAG), vector databases, or long-term retrieval

Instead of attempting to recall every detail, the design emphasizes **structured memory and controlled summarization**, reflecting how production LLM systems manage context under real constraints.

---

## 🧠 4. Solution Overview: Layered Memory Compression

### 4.1 Inspiration from Production LLM Systems

Modern LLM systems (e.g., ChatGPT) do not operate on raw conversation text alone.

Each response is generated from a **structured context package** composed of multiple layers with different lifetimes and priorities, including:

- system and developer instructions  
- session-level metadata  
- long-term user memory  
- summarized representations of prior conversations  
- a sliding window of recent dialogue turns  

These layers are assembled dynamically at inference time to maintain context awareness under strict token limits.

---

### 4.2 Layered Approach in This Project

Inspired by this architecture, the project adopts a **layered memory compression strategy**, decomposing conversation context by **stability and relevance**:

```
Original Conversation
        ↓
L01 – Long-termUser Memory (stable facts)
        ↓
L02 – ConversationSummary (semantic abstraction)
        ↓
L03 – Recent ContextWindow (recency)
        ↓
Final Compressed Context
```

Each layer serves a distinct purpose and is compressed using an appropriate strategy, balancing:

- information retention
- token efficiency
- interpretability

---

### Repository Organization

The repository structure reflects this layered design:

```
AI_compression/
│
├── src/
│   ├── L01_memory_extractor.py   # Long-term user memory extraction
│   ├── L02_summarizer.py         # Conversation summarization (rule / llm / auto)
│   ├── L03_assembler.py          # Context assembly with fixed sliding window
│
├── data/
│   └── conversation.json         # Input conversation (provided test data)
│
├── output/
│   ├── compressed_context_rule.json  # Rule-based compression result
│   └── compressed_context_llm.json   # LLM-based compression result (offline)
│
├── run.py                        # CLI pipeline execution
├── app.py                        # Streamlit visualization (no live inference)
└── README.md

```

Compression logic, evaluation artifacts, and visualization are **explicitly separated** to ensure reproducibility and clarity.

---

## ⚙️ 5. Compression Pipeline

The compression process follows a **deterministic, multi-stage pipeline** designed to enforce information prioritization under a fixed token budget.

---

### 5.1 L01 – Long-term Fact Extraction

**Purpose**

Extract **stable, decision-critical facts** such as company profile, hard constraints, and non-negotiable requirements.

**Engineering Decision**

- Implemented using **rule-based logic**
- No LLM usage

**Rationale**

Stable facts should persist across turns and sessions. Deterministic extraction ensures:

- predictability
- debuggability
- no hallucination

The output of this stage forms the **highest-priority memory layer**.

---

### 5.2 L02 – Conversation Summarization

**Purpose**

Compress the full dialogue into a **decision-oriented summary** capturing:

- evolving requirements
- pain points
- preferences
- timeline constraints

**Execution Modes**

Summarization supports three modes:

| Mode | Description |
| --- | --- |
| `rule` | Fully deterministic, rule-based baseline |
| `llm` | LLM-based semantic summarization，used gpt-5-mini |
| `auto` | Uses `llm` if API key is available, otherwise falls back to `rule` |

**Engineering Rationale**

- `rule` mode provides a transparent and reproducible baseline
- `llm` mode isolates semantic abstraction to a single layer
- `auto` mode ensures robustness in environments without API access

> LLM-based summaries are generated offline using a locally configured API key.
> 
> 
> No live API calls are performed in the repository or Streamlit app.
> 

---

### 5.3 L03 – Context Assembly (Fixed Sliding Window)

**Purpose**

Assemble the final compressed context by combining:

- long-term user memory
- conversation summary
- recent dialogue turns

**Design Decision**

- A **fixed sliding window of the last 4 turns** is retained
- This is a system-level design choice, not a tunable parameter

**Rationale**

Fixing the window size:

- balances recency and stability
- prevents uncontrolled context growth
- ensures fair comparison across summarization strategies

---

### Output Artifacts

The final outputs are saved as:

- `compressed_context_rule.json`
- `compressed_context_llm.json`

Each file contains:

- extracted user memory
- summarized conversation context
- the last 4 dialogue turns

These artifacts represent the **actual context injected into an LLM under token constraints** and are the direct subject of evaluation.

---

### Running the Pipeline

```bash
python run.py --mode rule
python run.py --mode llm
python run.py --mode auto
```

All modes execute the same L01–L03 pipeline, differing only in the summarization strategy.

---

## 📊 6. Evaluation Methodology (Core Section)

Evaluation focuses on whether the system preserves **decision-critical information under a fixed token budget**, rather than surface-level textual similarity.

Two explicit metrics are used.

---

## 6.1 Metric 1 – Token Budget Compliance

### Method

Token usage is approximated using a character-based heuristic:

```
Estimated tokens ≈numberof characters /2
```

This approximation is sufficient for **relative comparison**, as all variants share the same language and format.

### Results

| Version | Characters | Approx. Tokens | Reduction |
| --- | --- | --- | --- |
| Original conversation | 2,759 | ~1,380 | — |
| Rule-based compression | 929 | ~465 | ↓ 66.3% |
| LLM-based compression | 840 | ~420 | ↓ 69.6% |

**Observation**

Both compression strategies achieve over **65% reduction**, satisfying the token constraint.

---

## 6.2 Metric 2 – Weighted Information Retention

### Importance Weighting

Ground-truth key information items are **not equally important**.

They are categorized into three tiers:

| Tier | Description | Weight |
| --- | --- | --- |
| Tier 1 | Hard constraints (feasibility) | 3 |
| Tier 2 | Core requirements (solution fit) | 2 |
| Tier 3 | Soft / future signals | 1 |

### Scoring Rules

| Status | Score |
| --- | --- |
| Preserved | 1.0 |
| Partially preserved | 0.5 |
| Missing | 0.0 |

Final score:

```
WeightedRetentionScore
= Σ (item_score × item_weight) / Σ item_weight
```

---

### Results

Total weighted importance: **31**

| Ground Truth Key Information | Rule-based | LLM-based |
| --- | --- | --- |
| B2B enterprise | ✅ Preserved | ✅ Preserved |
| Company size: ~200 people | ❌ Missing | ✅ Preserved |
| Sales team size: ~50 people | ❌ Missing | ✅ Preserved |
| Excel-based CRM causes conflicts and reporting issues | ⚠️ Partial | ✅ Preserved |
| Mobile support required | ❌ Missing | ✅ Preserved |
| Enterprise WeChat integration required | ❌ Missing | ✅ Preserved |
| Budget: ~20万 / year | ✅ Preserved | ✅ Preserved |
| Cloud deployment required | ⚠️ Partial | ✅ Preserved |
| No internal IT team | ❌ Missing | ✅ Preserved |
| Data must be stored in China (hard constraint) | ✅ Preserved | ✅ Preserved |
| Expected launch before Spring Festival (~2 months) | ⚠️ Partial | ✅ Preserved |
| Emphasis on usability for diverse sales team | ❌ Missing | ❌ Missing |
| Dedicated post-sales support required | ⚠️ Partial | ❌ Missing |
| Potential approval workflow needed in ~6 months | ⚠️ Partial | ✅ Preserved |

| Version | Weighted Retention Score |
| --- | --- |
| Rule-based | **0.45** |
| LLM-based(gpt-5-mini) | **0.94** |

---

## 6.3 Interpretation

- **Rule-based compression**
    - Preserves explicit hard constraints
    - Misses numerical facts, implicit requirements, and future considerations
- **LLM-based compression**
    - Achieves near-complete retention across all importance tiers
    - Improves semantic abstraction under the same token budget

---

## ✊ 7. Final Concl

Under comparable token budgets (~70% reduction), **LLM-based compression significantly outperforms rule-based compression in weighted information retention (0.94 vs 0.45)**.

This demonstrates that effective memory compression depends on **semantic understanding of decision-critical information**, not surface-level text reduction.

By isolating LLM usage to the summarization layer, the system improves compression quality while maintaining **architectural transparency and engineering control**.

---

## 🧩 8. Streamlit Visualization

A multi-page Streamlit application (`app.py`) is provided to:

- visualize each layer of the compression pipeline
- inspect intermediate outputs
- present evaluation metrics and comparisons

The app performs **no live inference** and depends only on pre-generated outputs, ensuring reproducibility and sability.

---

## 📈 9. Limitations & Future Work

Overall, the project is a simplified project to just show the structure and methods. So it’s not mature.

- L01 relies on heuristic rules and may miss unseen patterns
- Evaluation is conducted on a single conversa
- The only used LLM model is gpt-5-mini, for further evaluation, more models and prompt should be select through benchmark testing to improve performance.
- Future work may include:
    - automatic importance classification
    - larger evaluation datasets
    - adaptive window strategies
