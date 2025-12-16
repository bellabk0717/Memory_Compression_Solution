from streamlit import json

# read a conversation from a JSON file
def load_conversation(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# save a conversation to a JSON file
def save_json(data: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# extract chat messages from a conversation
def get_messages(conversation: dict):
    return conversation["messages"]
