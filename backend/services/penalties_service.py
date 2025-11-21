import json, os
from datetime import datetime, timezone

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/penalties.json")


class PenaltiesService:
    def __init__(self, path: str | None = None, loader=None, saver=None, now=None):
        self.file = path or DATA_PATH
        self._loader = loader or self._load_from_file
        self._saver = saver or self._save_to_file
        self._now = now or (lambda: datetime.now(timezone.utc))

        # Only touch the filesystem when using default file storage.
        if loader is None and saver is None:
            self._ensure_file_exists()

    def _load(self):
        return self._loader()

    def _save(self, data):
        self._saver(data)

    def _ensure_file_exists(self):
        if not os.path.exists(self.file):
            with open(self.file, "w") as f:
                json.dump([], f)

    def _load_from_file(self):
        with open(self.file, "r") as f:
            return json.load(f)

    def _save_to_file(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=4)

    def _next_penalty_id(self, data):
        return (data[-1]["penalty_id"] + 1) if data else 1

    ## This has ids as integers inconsistent with other schema
    def add_penalty(self, user_id: int, reason: str, issued_by: int, source_flag_id: int | None = None):
        data = self._load()
        new_penalty = {
            "penalty_id": self._next_penalty_id(data),
            "user_id": user_id,
            "issued_by": issued_by,                 # ← record admin who issued it
            "reason": reason,
            "source_flag_id": source_flag_id,       # ← optional link to a flag
            "date_issued": self._now().isoformat(),
            "active": True,
            "date_revoked": None,
            "revoked_by": None
        }
        data.append(new_penalty)
        self._save(data)
        return new_penalty

    def get_all(self):
        return self._load()

    def get_for_user(self, user_id: int):
        return [p for p in self._load() if p["user_id"] == user_id]

    def deactivate_penalty(self, penalty_id: int, revoked_by: int):
        data = self._load()
        for p in data:
            if p["penalty_id"] == penalty_id and p["active"]:
                p["active"] = False
                p["date_revoked"] = self._now().isoformat()
                p["revoked_by"] = revoked_by             # ← record admin who revoked
                self._save(data)
                return p
        return None

    def update_penalty(self, penalty_id: int, *, reason=None, issued_by=None, source_flag_id=None):
        data = self._load()
        for p in data:
            if p["penalty_id"] == penalty_id:
                if reason is not None:
                    p["reason"] = reason
                if issued_by is not None:
                    p["issued_by"] = issued_by
                if source_flag_id is not None:
                    p["source_flag_id"] = source_flag_id
                self._save(data)
                return p
        return None
