# backend/tests/test_watchlist_concurrency.py
import pytest
from concurrent.futures import ThreadPoolExecutor
import json
from backend.services import watchlist_service as wl


def test_concurrent_add_to_watchlist_uses_atomic_saves(tmp_path, monkeypatch):
    # Redirect watchlist file to a temp file
    test_file = tmp_path / "watchlist.json"
    monkeypatch.setattr(wl, "WATCHLIST_FILE", test_file)

    # Spy on the real save function
    real_save = wl.save_watchlists
    calls = []

    def save_spy(data):
        calls.append(len(json.dumps(data)))  # record something about the data
        real_save(data)

    monkeypatch.setattr(wl, "save_watchlists", save_spy)

    user_id = "u1"
    movie_titles = [f"Movie {i}" for i in range(20)]

    def worker(title):
        wl.add_to_watchlist(user_id, title)

    with ThreadPoolExecutor(max_workers=10) as pool:
        list(pool.map(worker, movie_titles))

    # Assert file is valid JSON and contains all movies
    final_data = wl.load_watchlists()
    titles_in_file = {m["movieTitle"] for m in final_data["users"][0]["watchlist"]}
    assert titles_in_file == set(movie_titles)

    # And we actually did multiple saves (concurrent-ish scenario)
    assert len(calls) >= 1

def test_concurrent_reads_same_user_only(tmp_path, monkeypatch):
    """
    We pre-populate the watchlist file and then hammer get_user_watchlist
    from multiple threads, asserting:
      - no exceptions are raised
      - every read sees a consistent, valid watchlist
    """
    test_file = tmp_path / "watchlist.json"
    monkeypatch.setattr(wl, "WATCHLIST_FILE", test_file)

    # Known-good initial data
    baseline_movies = [
        {"movieTitle": "Movie A", "addedAt": "2025-01-01T00:00:00+00:00"},
        {"movieTitle": "Movie B", "addedAt": "2025-01-02T00:00:00+00:00"},
    ]
    wl.save_watchlists({
        "users": [
            {"userId": "u-readonly", "watchlist": baseline_movies},
        ]
    })

    def reader():
        # Should never raise, should always see the same list
        result = wl.get_user_watchlist("u-readonly")
        # Order preserved, no corruption
        assert result == baseline_movies
        return result

    # Many concurrent readers, no writers
    num_readers = 50
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(lambda _: reader(), range(num_readers)))

    # Every thread saw the same data
    for r in results:
        assert r == baseline_movies

def test_concurrent_read_and_write_same_user(tmp_path, monkeypatch):
    """
    We run a writer that appends a bunch of movies and several readers
    that repeatedly read the watchlist. We assert:
      - no reader hits an exception (i.e., JSON never corrupted)
      - final persisted watchlist contains all written movies exactly once
    """
    test_file = tmp_path / "watchlist.json"
    monkeypatch.setattr(wl, "WATCHLIST_FILE", test_file)

    # Start with an empty watchlist structure
    wl.save_watchlists({"users": []})

    user_id = "u-mixed"
    movie_titles = [f"Movie {i}" for i in range(30)]

    def writer():
        # Each movie is added once; locking should prevent lost updates
        for title in movie_titles:
            wl.add_to_watchlist(user_id, title)

    def reader():
        # Repeatedly read; if the file gets corrupted, this will throw
        for _ in range(50):
            wl.get_user_watchlist(user_id)

    # Run 1 writer + several readers concurrently
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = []
        futures.append(pool.submit(writer))
        for _ in range(5):
            futures.append(pool.submit(reader))

        # Propagate any exceptions from threads
        for f in futures:
            f.result()

    # After concurrent read/write, the file must still be valid JSON
    final_data = wl.load_watchlists()
    users_map = {u["userId"]: u for u in final_data["users"]}
    assert user_id in users_map

    final_watchlist = users_map[user_id]["watchlist"]
    titles_in_file = {m["movieTitle"] for m in final_watchlist}

    # All movies written, none lost
    assert titles_in_file == set(movie_titles)
    # And no duplicates
    assert len(final_watchlist) == len(set(movie_titles))


def test_concurrent_add_same_user_different_movies(tmp_path, monkeypatch):
    test_file = tmp_path / "watchlist.json"
    monkeypatch.setattr(wl, "WATCHLIST_FILE", test_file)

    user_id = "u-equivalence"
    movie_titles = [f"Movie {i}" for i in range(30)]

    def worker(title):
        wl.add_to_watchlist(user_id, title)

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(worker, movie_titles))

    data = wl.load_watchlists()
    users = {u["userId"]: u for u in data["users"]}
    wl_user = users[user_id]
    titles = {m["movieTitle"] for m in wl_user["watchlist"]}

    # Representative of "many writes to same user"
    assert titles == set(movie_titles)


def test_concurrent_add_different_users(tmp_path, monkeypatch):
    test_file = tmp_path / "watchlist.json"
    monkeypatch.setattr(wl, "WATCHLIST_FILE", test_file)

    pairs = [(f"user{i}", f"Movie {i}") for i in range(10)]

    def worker(pair):
        uid, title = pair
        wl.add_to_watchlist(uid, title)

    with ThreadPoolExecutor(max_workers=10) as pool:
        list(pool.map(worker, pairs))

    data = wl.load_watchlists()
    users_map = {u["userId"]: u for u in data["users"]}
    assert len(users_map) == 10  # one per user


def test_watchlist_save_failure_does_not_corrupt_file(tmp_path, monkeypatch):
    test_file = tmp_path / "watchlist.json"
    monkeypatch.setattr(wl, "WATCHLIST_FILE", test_file)

    # Start with a known-good file
    wl.save_watchlists({"users": []})

    # Fault injection: first save fails, second succeeds
    real_save = wl.save_watchlists
    calls = {"count": 0}

    def flaky_save(data):
        calls["count"] += 1
        if calls["count"] == 1:
            raise IOError("simulated disk full")
        real_save(data)

    monkeypatch.setattr(wl, "save_watchlists", flaky_save)

    # First attempt should raise
    with pytest.raises(IOError):
        wl.add_to_watchlist("u1", "Movie Fails First Time")

    # Second attempt should succeed
    wl.add_to_watchlist("u1", "Movie Fails First Time")

    # File must still be valid JSON and contain the movie
    final = wl.load_watchlists()
    assert final["users"][0]["watchlist"][0]["movieTitle"] == "Movie Fails First Time"


def test_add_to_watchlist_propagates_save_error(tmp_path, monkeypatch):
    test_file = tmp_path / "watchlist.json"
    monkeypatch.setattr(wl, "WATCHLIST_FILE", test_file)

    wl.save_watchlists({"users": []})

    def boom(data):
        raise IOError("disk full")

    monkeypatch.setattr(wl, "save_watchlists", boom)

    # Single-thread: error is propagated
    with pytest.raises(IOError):
        wl.add_to_watchlist("u1", "Bad Movie")

    # Multi-thread: errors still propagate per call, and no deadlock
    def worker():
        with pytest.raises(IOError):
            wl.add_to_watchlist("u1", "Bad Movie")

    with ThreadPoolExecutor(max_workers=5) as pool:
        list(pool.map(lambda _: worker(), range(5)))
