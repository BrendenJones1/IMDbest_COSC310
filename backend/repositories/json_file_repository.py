import json
import os
from pathlib import Path
from typing import Dict, Any


class JsonFileRepository:
    """
    Small reusable helper for repositories that persist a JSON document
    to disk at a fixed path.
    """

    def __init__(self, file_path: str, default_data: Dict[str, Any]) -> None:
        self.path = Path(file_path)
        self.default_data = default_data
        self._ensure_file()

    def _ensure_file(self) -> None:
        """
        Ensure the JSON file exists on disk with at least the default
        structure.
        """
        if not self.path.exists():
            os.makedirs(self.path.parent, exist_ok=True)
            self._write_raw(self.default_data)

    def _read_raw(self) -> Dict[str, Any]:
        """
        Load raw JSON from disk. If anything goes wrong, fall back to
        the default structure.
        """
        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return dict(self.default_data)

        if not isinstance(data, dict):
            return dict(self.default_data)

        return data

    def _write_raw(self, data: Dict[str, Any]) -> None:
        """
        Write the given dictionary to disk as pretty-printed JSON.
        """
        os.makedirs(self.path.parent, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load(self) -> Dict[str, Any]:
        """
        Public API: load the JSON document with defaults applied.
        """
        return self._read_raw()

    def save(self, data: Dict[str, Any]) -> None:
        """
        Public API: persist the JSON document back to disk.
        """
        self._write_raw(data)
