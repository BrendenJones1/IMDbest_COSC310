# backend/services/flags_service.py
import os
from datetime import datetime

from backend.repositories.flags_repo import FlagsRepository

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/flags.json")


class FlagsService:
    def __init__(self, path: str | None = None, repo: FlagsRepository | None = None):
        """
        Provide a high-level interface for managing moderation flags backed by a JSON file.
        """
        self.file = path or DATA_PATH
        self.repo = repo or FlagsRepository(self.file)

    def _load(self):
        """
        Load the current list of flags from the repository, re-binding if the file path changed.
        """
        if self.repo.file_path != self.file:
            self.repo = FlagsRepository(self.file)  # keep repository aligned with the active file
        return self.repo.load()

    def _save(self, data):
        """
        Persist the given flag collection to the backing store, ensuring the repository is in sync.
        """
        if self.repo.file_path != self.file:
            self.repo = FlagsRepository(self.file)
        self.repo.save(data)

    def add_flag(self, review_id, flagger_id, flagged_user_id, reason):
        """
        Create and store a new flag for a review, initializing it in the pending state.
        """
        data = self._load()
        new_flag = {
            "flag_id": len(data) + 1,
            "review_id": review_id,
            "flagger_id": flagger_id,
            "flagged_user_id": flagged_user_id,
            "reason": reason,
            "status": "pending",
            "date_created": datetime.now().isoformat(),
        }
        data.append(new_flag)
        self._save(data)
        return new_flag

    def get_all_flags(self):
        """
        Return the full collection of stored flags.
        """
        return self._load()

    def update_flag_status(self, flag_id, new_status):
        """
        Update the status of a specific flag and return the updated record if found.
        """
        data = self._load()
        for flag in data:
            if flag["flag_id"] == flag_id:
                flag["status"] = new_status
                self._save(data)
                return flag
        return None

    def get_pending_flags(self):
        """
        Retrieve all flags that are still marked as pending.
        """
        return [f for f in self._load() if f["status"] == "pending"]
