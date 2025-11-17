import json, os
from pathlib import Path
from typing import List, Dict, Any, Optional

USERS_FILE = Path(__file__).resolve().parents[1] / "data" / "users.json"


class UserRepository:
    """File-based user repository used by services and monkeypatched in tests."""

    def __init__(self, users_file: Path = USERS_FILE) -> None:
        self.users_file = users_file

    def load_users(self) -> List[Dict[str, Any]]:
        if not self.users_file.exists():
            return []
        with self.users_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save_users(self, users: List[Dict[str, Any]]) -> None:
        tmp = self.users_file.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.users_file)

    # Convenience helpers retained for compatibility
    def get_all_users(self) -> List[Dict[str, Any]]:
        return self.load_users()

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        email_lower = email.strip().lower()
        for user in self.load_users():
            if user.get("email", "").lower() == email_lower:
                return user
        return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        for user in self.load_users():
            if user.get("id") == user_id:
                return user
        return None

    def upsert_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        users = self.load_users()
        for idx, existing in enumerate(users):
            if existing.get("id") == user.get("id"):
                users[idx] = user
                break
        else:
            users.append(user)
        self.save_users(users)
        return user


# Default repository instance used by services
user_repository = UserRepository()

# Backwards-compatible module-level helpers
def load_users() -> List[Dict[str, Any]]:
    return user_repository.load_users()


def save_users(users: List[Dict[str, Any]]) -> None:
    return user_repository.save_users(users)


def get_all_users() -> List[Dict[str, Any]]:
    return user_repository.get_all_users()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    return user_repository.get_user_by_email(email)


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    return user_repository.get_user_by_id(user_id)


def upsert_user(user: Dict[str, Any]) -> Dict[str, Any]:
    return user_repository.upsert_user(user)
