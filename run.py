import argparse
import json
import os

from src.L01_memory_extractor import extract_user_memory
from src.L02_summarizer import summarize_conversation
from src.L03_assembler import assemble_context


# ============================================================
# Utility functions
# 工具函数
# ============================================================

def load_conversation(path: str):
    """
    Load conversation JSON from disk.
    从磁盘加载对话数据
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_output(data, path: str):
    """
    Save output JSON to disk.
    Automatically create parent directory if not exists.

    将结果保存为 JSON，如果目录不存在则自动创建
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# Main pipeline
# 主流程
# ============================================================

def main():
    # -------------------------------
    # Parse command line arguments
    # 解析命令行参数
    # -------------------------------
    parser = argparse.ArgumentParser(
        description="LLM Memory Compression Pipeline (Task B)"
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "llm", "rule"],
        default="auto",
        help="Summarization mode: auto | llm | rule"
    )
    args = parser.parse_args()

    print(f"🚀 Running memory compression pipeline (mode = {args.mode})")

    # -------------------------------
    # Load input conversation
    # 加载原始对话
    # -------------------------------
    conversation = load_conversation("data/conversation.json")
    messages = conversation.get("messages", [])

    # -------------------------------
    # L01: Extract user memory
    # 提取长期稳定事实
    # -------------------------------
    user_memory = extract_user_memory(messages)

    # -------------------------------
    # L02: Summarize conversation
    # 生成对话摘要（显式模式控制）
    # -------------------------------
    conversation_summary = summarize_conversation(
        messages,
        mode=args.mode
    )

    # -------------------------------
    # L03: Assemble final context
    # 组装最终压缩上下文
    # -------------------------------
    compressed_context = assemble_context(
        user_memory=user_memory,
        conversation_summary=conversation_summary,
        messages=messages,
        max_recent_turns=4
    )

    # -------------------------------
    # Save output
    # 保存结果
    # -------------------------------
    output_path = f"output/compressed_context_{args.mode}.json"
    save_output(compressed_context, output_path)

    print("✅ Compression pipeline finished successfully.")
    print(f"📄 Output saved to {output_path}")


# ============================================================
# Entry point
# 程序入口
# ============================================================

if __name__ == "__main__":
    main()

