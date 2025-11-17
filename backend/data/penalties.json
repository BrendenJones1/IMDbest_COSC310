import json, os
from datetime import datetime, timezone

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/penalties.json")

class PenaltiesService:
    def __init__(self, path: str | None = None):
        self.file = path or DATA_PATH
        if not os.path.exists(self.file):
            with open(self.file, "w") as f:
                json.dump([], f)

    def _load(self):
        with open(self.file, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=4)

    ## This has ids as integers inconsistent with other schema
    def add_penalty(self, user_id: int, reason: str, issued_by: int, source_flag_id: int | None = None):
        data = self._load()
        new_penalty = {
            "penalty_id": (data[-1]["penalty_id"] + 1) if data else 1,
            "user_id": user_id,
            "issued_by": issued_by,                 # ← record admin who issued it
            "reason": reason,
            "source_flag_id": source_flag_id,       # ← optional link to a flag
            "date_issued": datetime.now(timezone.utc).isoformat(),
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
                p["date_revoked"] = datetime.now(timezone.utc).isoformat()
                p["revoked_by"] = revoked_by             # ← record admin who revoked
                self._save(data)
                return p
        return None