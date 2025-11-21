import json, os
from pathlib import Path
from typing import List, Dict, Any, Optional
from threading import Lock
from contextlib import contextmanager


class UserRepository:
    _lock = Lock()


    def __init__(self, users_file: Optional[Path] = None) -> None:
        # default to backend/data/users.json (adjust parents[...] if needed)
        self.users_file = users_file or Path(__file__).resolve().parents[1] / "data" / "users.json"

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

    @contextmanager
    def transaction(self):
        """
        Atomic read-modify-write on users.json.
        Only saves if the with-block exits without error.
        """
        with self._lock:
            users = self.load_users() or []
            try:
                yield users
                self.save_users(users)
            except Exception:
                # don't save on error, just propagate
                raise

# shared instance used by the app
user_repository = UserRepository()
