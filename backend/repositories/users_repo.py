import json, os
from pathlib import Path
from typing import List, Dict, Any, Optional

USERS_FILE = Path(__file__).resolve().parents[1] / "data" / "users.json"


def load_users() -> List[Dict[str, Any]]:
    if not USERS_FILE.exists():
        return []
    with USERS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users: List[Dict[str, Any]]) -> None:
    tmp = USERS_FILE.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    os.replace(tmp, USERS_FILE)


def get_all_users() -> List[Dict[str, Any]]:
    return load_users()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    email_lower = email.strip().lower()
    for user in load_users():
        if user.get("email", "").lower() == email_lower:
            return user
    return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    for user in load_users():
        if user.get("id") == user_id:
            return user
    return None


def upsert_user(user: Dict[str, Any]) -> Dict[str, Any]:
    users = load_users()
    for idx, existing in enumerate(users):
        if existing.get("id") == user.get("id"):
            users[idx] = user
            break
    else:
        users.append(user)
    save_users(users)
    return user
