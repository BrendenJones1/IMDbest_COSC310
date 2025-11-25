from typing import Dict, Any

from backend.repositories.json_file_repository import JsonFileRepository


class WatchlistRepository(JsonFileRepository):
    """
    Repository for the watchlist store, backed by a JSON file.

    The underlying JSON structure is normalised to:

        {"users": [...]}

    All JSON file I/O is delegated to JsonFileRepository.
    """

    def __init__(self, file_path: str) -> None:
        # We keep the same public constructor signature but reuse the
        # shared JSON file handling in the base class.
        super().__init__(file_path=file_path, default_data={"users": []})

    # If needed in the future, watchlist-specific helpers can be added here,
    # for example methods to get or update a single user entry.
    #
    # For now, we simply inherit load()/save() from JsonFileRepository.
