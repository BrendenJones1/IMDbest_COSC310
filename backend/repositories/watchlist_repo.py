import json
import os
from typing import List, Dict, Any


class WatchlistRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        """Ensure the JSON file exists and has correct structure."""
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                # Standard watchlist structure
                json.dump({"users": []}, f, indent=4)

    def load(self) -> Dict[str, Any]:
        """Load the watchlist JSON as a dictionary."""
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Normalize data structure
        if "users" not in data or not isinstance(data["users"], list):
            data = {"users": []}

        return data

    def save(self, data: Dict[str, Any]) -> None:
        """Save updated watchlist data back to disk."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
