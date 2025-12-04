import json
import os
from threading import RLock
from typing import List

# Module-level lock to protect file I/O across all PenaltiesRepository instances
_PENALTIES_REPO_LOCK = RLock()


class PenaltiesRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        """
        Ensure the penalties JSON file and its parent directory exist.
        """
        # Directory creation is cheap but not thread-safe on all platforms, so protect it too.
        with _PENALTIES_REPO_LOCK:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            if not os.path.exists(self.file_path):
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f)

    def load(self) -> List[dict]:
        """
        Load the list of penalties from disk in a thread-safe way.
        """
        with _PENALTIES_REPO_LOCK:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)

    def save(self, data: List[dict]) -> None:
        """
        Save penalties to disk atomically:
        - write to a temp file
        - replace the original with os.replace (atomic on most OSes)
        All guarded by a lock to avoid partial writes / concurrent truncation.
        """
        tmp_path = self.file_path + ".tmp"
        with _PENALTIES_REPO_LOCK:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            os.replace(tmp_path, self.file_path)
