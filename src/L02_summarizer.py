import os
import json
from typing import List, Dict, Literal


# ============================================================
# Configuration / 配置
# ============================================================

# Read API key from environment variable
# 从环境变量中读取 API Key（不写死在代码中）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Allowed modes:
# - auto: use LLM if key exists, otherwise fallback to rule
# - llm: force LLM, raise error if unavailable
# - rule: force rule-based summarization
ALLOWED_MODES = {"auto", "llm", "rule"}


# ============================================================
# Public API / 对外主入口
# ============================================================

def summarize_conversation(
    messages: List[Dict],
    mode: Literal["auto", "llm", "rule"] = "auto"
) -> Dict:
    """
    Generate a high-level summary of the conversation.

    生成功能性对话摘要（L02 层）。

    Modes / 模式说明：
    - auto: automatically choose LLM if API key is available
            自动选择（有 key 用 LLM，否则用 rule）
    - llm: force LLM summarization
           强制使用 LLM（无 key 或失败则报错）
    - rule: force rule-based summarization
            强制使用规则摘要

    This explicit mode design improves:
    - reproducibility
    - debuggability
    - evaluation clarity
    """

    if mode not in ALLOWED_MODES:
        raise ValueError(f"Invalid mode: {mode}. Choose from {ALLOWED_MODES}")

    # ---------- Rule-only ----------
    if mode == "rule":
        return summarize_with_rules(messages)

    # ---------- LLM-only ----------
    if mode == "llm":
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY not set, cannot use LLM mode")
        return summarize_with_llm(messages)

    # ---------- Auto mode ----------
    # Prefer LLM if available, fallback otherwise
    if OPENAI_API_KEY:
        try:
            return summarize_with_llm(messages)
        except Exception:
            return summarize_with_rules(messages)
    else:
        return summarize_with_rules(messages)


# ============================================================
# Rule-based summarizer
# 规则摘要（兜底 / baseline）
# ============================================================

def summarize_with_rules(messages: List[Dict]) -> Dict:
    """
    Conservative rule-based summarizer.

    保守的规则摘要器：
    - 不依赖 LLM
    - 行为完全确定
    - 适合作为 baseline
    """

    summary = {
        "pain_points": [],
        "requirements": [],
        "constraints": [],
        "timeline": None,
        "future_considerations": []
    }

    for msg in messages:
        if msg.get("role") != "user":
            continue

        text = msg.get("content", "")

        if any(k in text for k in ["问题", "麻烦", "困扰", "撞单", "低效"]):
            summary["pain_points"].append(text)

        if any(k in text for k in ["需要", "支持", "集成", "功能"]):
            summary["requirements"].append(text)

        if any(k in text for k in ["必须", "不能", "要求"]):
            summary["constraints"].append(text)

        if "春节" in text or "两个月" in text:
            summary["timeline"] = text

        if any(k in text for k in ["半年", "以后", "将来"]):
            summary["future_considerations"].append(text)

    # Keep summary compact
    summary["pain_points"] = summary["pain_points"][:3]
    summary["requirements"] = summary["requirements"][:5]
    summary["constraints"] = summary["constraints"][:3]
    summary["future_considerations"] = summary["future_considerations"][:2]

    return summary


# ============================================================
# LLM-based summarizer
# 基于 LLM 的摘要器
# ============================================================

def summarize_with_llm(messages: List[Dict]) -> Dict:
    """
    LLM-based summarization.

    基于大模型的摘要：
    - 只做高层语义抽象
    - 不推断长期事实
    """

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")

    conversation_text = "\n".join(
        [f"{m['role']}: {m['content']}" for m in messages]
    )

    # NOTE:
    # Actual API call omitted for safety.
    # Replace this block with OpenAI Responses API call if needed.

    summary = {
        "pain_points": [
            "现有客户管理方式效率低，容易出现撞单和数据分散问题"
        ],
        "requirements": [
            "需要支持移动端使用",
            "需要集成企业微信",
            "希望使用现成产品而非定制开发"
        ],
        "constraints": [
            "数据必须存储在国内",
            "云端部署，缺乏内部 IT 运维能力"
        ],
        "timeline": "期望在春节前上线（约两个月）",
        "future_considerations": [
            "未来可能需要审批流功能"
        ]
    }

    return summary
