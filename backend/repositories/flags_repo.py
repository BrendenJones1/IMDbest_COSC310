# backend/repositories/flags_repo.py
import json
import os
from typing import Any, List
from threading import RLock
from contextlib import contextmanager


class FlagsRepository:
    # Shared lock for all FlagsRepository instances in this process
    _lock = RLock()

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def load(self) -> List[dict]:
        """
        Load current flags from disk.
        """
        with self._lock:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)

    def save(self, data: List[dict]) -> None:
        """
        Atomically write flags to disk using a temp file + os.replace.
        """
        tmp_path = self.file_path + ".tmp"
        with self._lock:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            os.replace(tmp_path, self.file_path)

    @contextmanager
    def transaction(self):
        """
        Optional helper for atomic read-modify-write, if you want it later.
        Not required by current FlagsService/tests.
        """
        with self._lock:
            data = self.load()
            try:
                yield data
                self.save(data)
            except Exception:
                raise
