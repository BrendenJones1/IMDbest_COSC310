import json, os
from pathlib import Path
from typing import List, Dict, Any

USERS_FILE = Path(__file__).resolve().parents[1] / "data" / "users.json"

def load_users() -> List[Dict[str, Any]]:
    if not USERS_FILE.exists():
        return []
    with USERS_FILE.open("r", encoding="utf-8") as f:
        json.load(f)

def save_users(users: List[Dict[str, Any]]) -> None:
    tmp = USERS_FILE.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    os.replace(tmp, USERS_FILE)
