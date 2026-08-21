SYSTEM_PROMPT = """You are a helpful assistant. Use the available tools when they
are useful or necessary. Base your answer on tool results when you call a tool.
Keep the final answer concise."""


def build_messages(history: list[dict], user_message: str) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend({"role": entry["role"], "content": entry["content"]} for entry in history)
    messages.append({"role": "user", "content": user_message})
    return messages
