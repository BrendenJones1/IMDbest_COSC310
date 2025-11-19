import os
from datetime import datetime, timezone

from backend.repositories.penalties_repo import PenaltiesRepository

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/penalties.json")


class PenaltiesService:
    def __init__(self, path: str | None = None, repo: PenaltiesRepository | None = None, now=None):
        self.file = path or DATA_PATH
        self._now = now or (lambda: datetime.now(timezone.utc))
        self.repo = repo or PenaltiesRepository(self.file)

    def _ensure_repo(self):
        if self.repo.file_path != self.file:
            self.repo = PenaltiesRepository(self.file)

    def _load(self):
        self._ensure_repo()
        data = self.repo.load()
        return data if isinstance(data, list) else []

    def _save(self, data):
        self._ensure_repo()
        self.repo.save(data)

    ## This has ids as integers inconsistent with other schema
    def add_penalty(self, user_id: int, reason: str, issued_by: int, source_flag_id: int | None = None):
        data = self._load()
        next_id = (data[-1]["penalty_id"] + 1) if data else 1
        new_penalty = {
            "penalty_id": next_id,
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
        return [p for p in self._load() if p.get("user_id") == user_id]

    def deactivate_penalty(self, penalty_id: int, revoked_by: int):
        data = self._load()
        for p in data:
            if p.get("penalty_id") == penalty_id and p.get("active"):
                p["active"] = False
                p["date_revoked"] = self._now().isoformat()
                p["revoked_by"] = revoked_by             # ← record admin who revoked
                self._save(data)
                return p
        return None

    def update_penalty(self, penalty_id: int, *, reason=None, issued_by=None, source_flag_id=None):
        data = self._load()
        for p in data:
            if p.get("penalty_id") == penalty_id:
                if reason is not None:
                    p["reason"] = reason
                if issued_by is not None:
                    p["issued_by"] = issued_by
                if source_flag_id is not None:
                    p["source_flag_id"] = source_flag_id
                self._save(data)
                return p
        return None
