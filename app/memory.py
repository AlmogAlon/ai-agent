import json
import os

import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
SESSION_TTL_SECONDS = 60 * 60 * 24  # 1 day

_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def _key(session_id: str) -> str:
    return f"session:{session_id}:history"


def get_history(session_id: str) -> list[dict]:
    raw = _client.get(_key(session_id))
    if not raw:
        return []
    return json.loads(raw)


def append_message(session_id: str, role: str, content: str) -> None:
    history = get_history(session_id)
    history.append({"role": role, "content": content})
    _client.set(_key(session_id), json.dumps(history), ex=SESSION_TTL_SECONDS)
