import json
import os
import uuid
from datetime import datetime, timezone

CONVERSATIONS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "conversations.json")


def _load():
    if not os.path.exists(CONVERSATIONS_FILE):
        return {}
    with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data):
    with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user_conversations(username):
    data = _load()
    user_convs = data.get(username, [])
    summaries = [
        {"id": c["id"], "title": c["title"], "updated_at": c["updated_at"]}
        for c in user_convs
    ]
    return sorted(summaries, key=lambda c: c["updated_at"], reverse=True)


def get_conversation_messages(username, conv_id):
    data = _load()
    for c in data.get(username, []):
        if c["id"] == conv_id:
            return c["messages"]
    return None


def create_conversation(username):
    data = _load()
    conv_id = f"conv_{uuid.uuid4().hex[:10]}"
    now = datetime.now(timezone.utc).isoformat()
    data.setdefault(username, []).append({
        "id": conv_id,
        "title": "New conversation",
        "created_at": now,
        "updated_at": now,
        "messages": []
    })
    _save(data)
    return conv_id


def append_message(username, conv_id, role, text, sources=None):
    data = _load()
    for c in data.get(username, []):
        if c["id"] == conv_id:
            message = {"role": role, "text": text}
            if sources is not None:
                message["sources"] = sources
            c["messages"].append(message)
            c["updated_at"] = datetime.now(timezone.utc).isoformat()
            if c["title"] == "New conversation" and role == "user":
                c["title"] = text[:40] + ("..." if len(text) > 40 else "")
            break
    _save(data)


def delete_conversation(username, conv_id):
    data = _load()
    user_convs = data.get(username, [])
    filtered = [c for c in user_convs if c["id"] != conv_id]
    if len(filtered) == len(user_convs):
        return False
    data[username] = filtered
    _save(data)
    return True