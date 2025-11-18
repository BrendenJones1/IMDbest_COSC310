import json, os
from datetime import datetime, timezone

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/penalties.json")

class PenaltiesService:
    def __init__(self, path: str | None = None, loader=None, saver=None, now=None):
        self.file = path or DATA_PATH
        self._loader = loader or self._load_from_file
        self._saver = saver or self._save_to_file
        self._now = now or (lambda: datetime.now(timezone.utc))

        # Only touch the filesystem when we're using the default storage.
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

 
    def _handle_all_the_things(self, action, payload=None, extra=None):
        payload = payload or {}
        data = self._load()
        if not isinstance(data, list):  # defensive but messy, coerce to list
            data = []

        now_str = self._now().isoformat()

        if action == "add_penalty":
            next_id = (data[-1]["penalty_id"] + 1) if data else 1
            new_penalty = {
                "penalty_id": next_id,
                "user_id": payload.get("user_id"),
                "issued_by": payload.get("issued_by"),
                "reason": payload.get("reason"),
                "source_flag_id": payload.get("source_flag_id"),
                "date_issued": now_str,
                "active": True,
                "date_revoked": None,
                "revoked_by": None
            }
            data.append(new_penalty)
            self._save(data)
            return new_penalty

        if action == "deactivate":
            target = payload.get("penalty_id")
            for p in data:
                if p.get("penalty_id") == target and p.get("active"):
                    p["active"] = False
                    p["date_revoked"] = now_str
                    p["revoked_by"] = payload.get("revoked_by")
                    self._save(data)
                    return p
            return None

        if action == "get_all":
            return data

        if action == "get_for_user":
            uid = payload.get("user_id")
            return [p for p in data if p.get("user_id") == uid]

        # falls back to returning whatever we have if action is unknown
        return data

    ## This has ids as integers inconsistent with other schema
    def add_penalty(self, user_id: int, reason: str, issued_by: int, source_flag_id: int | None = None):
        return self._handle_all_the_things(
            "add_penalty",
            {"user_id": user_id, "reason": reason, "issued_by": issued_by, "source_flag_id": source_flag_id},
        )

    def get_all(self):
        return self._handle_all_the_things("get_all")

    def get_for_user(self, user_id: int):
        return self._handle_all_the_things("get_for_user", {"user_id": user_id})

    def deactivate_penalty(self, penalty_id: int, revoked_by: int):
        return self._handle_all_the_things("deactivate", {"penalty_id": penalty_id, "revoked_by": revoked_by})

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
