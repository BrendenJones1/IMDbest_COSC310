import pytest

from backend.repositories.penalties_repo import PenaltiesRepository


def test_penalties_repo_load_fault(monkeypatch, tmp_path):
    file_path = tmp_path / "penalties.json"
    file_path.write_text("[]")
    repo = PenaltiesRepository(str(file_path))

    def boom(*args, **kwargs):
        raise ValueError("corrupted")

    monkeypatch.setattr("backend.repositories.penalties_repo.json.load", boom)

    with pytest.raises(ValueError):
        repo.load()


def test_penalties_repo_save_fault(monkeypatch, tmp_path):
    file_path = tmp_path / "penalties.json"
    repo = PenaltiesRepository(str(file_path))

    def boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr("backend.repositories.penalties_repo.json.dump", boom)

    with pytest.raises(OSError):
        repo.save([])
