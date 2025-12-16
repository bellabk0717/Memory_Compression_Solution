from typing import List, Dict


def assemble_context(
    user_memory: Dict,
    conversation_summary: Dict,
    messages: List[Dict],
    max_recent_turns: int = 4
) -> Dict:
    """
    Assemble the final compressed context for LLM input.

    构建最终用于 LLM 的压缩上下文（L03 层）。

    Responsibilities / 职责：
    - Assemble different memory layers into a single context package
      将不同记忆层组装成一个上下文包
    - Enforce prioritization between layers
      体现不同层级的优先级
    - Keep behavior deterministic and predictable
      保持行为确定性、可预测性

    Non-responsibilities / 明确不做的事：
    - Do NOT interpret semantics
      不理解语义
    - Do NOT infer or summarize content
      不推断、不总结
    - Do NOT call LLMs
      不调用大模型
    """

    # ------------------------------------------------
    # 1. Sliding window for recent messages
    #    最近对话窗口（短期上下文）
    # ------------------------------------------------
    # We keep only the most recent turns to preserve
    # conversational continuity.
    #
    # 只保留最近的若干轮对话，用于保持上下文连续性
    recent_messages = messages[-max_recent_turns:]

    # ------------------------------------------------
    # 2. Assemble layered context
    #    按层级组装上下文
    # ------------------------------------------------
    # Priority order:
    # 1) user_memory (highest priority)
    # 2) conversation_summary
    # 3) recent_messages (lowest priority)
    #
    # 优先级顺序：
    # 1）长期稳定事实
    # 2）阶段性摘要
    # 3）短期对话窗口
    context = {
        "user_memory": user_memory,
        "conversation_summary": conversation_summary,
        "recent_messages": recent_messages
    }

    return context
