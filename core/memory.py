import json
from pathlib import Path

# ---------- SHORT-TERM MEMORY ----------
short_term = []

def remember_short(user, aura):
    short_term.append({"user": user, "aura": aura})
    if len(short_term) > 10:
        short_term.pop(0)

def get_short_term():
    return short_term

def clear_short_term():
    short_term.clear()

# ---------- LONG-TERM MEMORY ----------
MEMORY_FILE = Path("memory/long_term.json")
MEMORY_FILE.parent.mkdir(exist_ok=True)

def normalize_key(key):
    """Helper to normalize memory keys."""
    return key.strip().lower().replace(" ", "_")

def save_fact(key, value):
    data = load_long_term()
    key = normalize_key(key)
    data[key] = value
    MEMORY_FILE.write_text(json.dumps(data, indent=2))

def load_long_term():
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())
    return {}

def recall_fact(key):
    key = normalize_key(key)
    return load_long_term().get(key)

def forget_fact(key):
    data = load_long_term()
    key = normalize_key(key)
    if key in data:
        del data[key]
        MEMORY_FILE.write_text(json.dumps(data, indent=2))
