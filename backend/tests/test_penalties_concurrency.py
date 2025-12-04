# backend/tests/test_penalties_concurrency.py

from concurrent.futures import ThreadPoolExecutor

import pytest

from backend.services.penalties_service import PenaltiesService

@pytest.fixture
def penalties_service_tmp(tmp_path):
    """
    Fresh PenaltiesService backed by a temp penalties.json for each test.
    Uses the default file-based loader/saver so we exercise locking + atomic writes.
    """
    penalties_file = tmp_path / "penalties.json"
    svc = PenaltiesService(path=str(penalties_file))
    return svc

def test_concurrent_penalties_read_only(penalties_service_tmp):
    """
    P1: Many concurrent read operations, no writers.

    Seed some penalties, then hammer get_all() and get_for_user()
    from multiple threads. Expect:
      - no exceptions
      - every reader sees a consistent snapshot
    """
    svc = penalties_service_tmp

    # Seed 5 users, 1 penalty each
    num_users = 5
    for uid in range(num_users):
        svc.add_penalty(user_id=uid, reason="seed", issued_by=999)

    def reader():
        all_p = svc.get_all()
        assert len(all_p) == num_users

        for uid in range(num_users):
            user_p = svc.get_for_user(uid)
            assert len(user_p) == 1
            assert user_p[0]["user_id"] == uid

    with ThreadPoolExecutor(max_workers=10) as pool:
        list(pool.map(lambda _: reader(), range(30)))

def test_concurrent_add_penalty_ids_unique_and_no_loss(penalties_service_tmp):
    """
    P2a: Many concurrent add_penalty() calls.

    Expect:
      - no JSON corruption
      - number of stored penalties == number of calls
      - penalty_id values are unique and form a consecutive range
        starting from 1 (based on the current implementation).
    """
    svc = penalties_service_tmp

    num_penalties = 50

    def worker(i: int):
        # User IDs can repeat; we only care about penalty_id sequence here
        svc.add_penalty(user_id=i % 5, reason=f"reason-{i}", issued_by=42)

    with ThreadPoolExecutor(max_workers=10) as pool:
        list(pool.map(worker, range(num_penalties)))

    all_p = svc.get_all()
    assert len(all_p) == num_penalties

    ids = [p["penalty_id"] for p in all_p]
    assert len(set(ids)) == len(ids)
    assert sorted(ids) == list(range(1, num_penalties + 1))

def test_concurrent_deactivate_penalty_only_once(penalties_service_tmp):
    """
    P2b: Many threads attempt to deactivate the same penalty concurrently.

    Expect:
      - exactly one call returns the updated penalty (active=False)
      - all other calls return None (already inactive)
      - final stored penalty is inactive with the correct revoked_by value
    """
    svc = penalties_service_tmp

    # Create a single penalty
    created = svc.add_penalty(user_id=1, reason="test", issued_by=99)
    pid = created["penalty_id"]

    def worker():
        result = svc.deactivate_penalty(penalty_id=pid, revoked_by=777)
        return result

    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(lambda _: worker(), range(20)))

    # Exactly one successful deactivation
    successes = [r for r in results if r is not None]
    assert len(successes) == 1
    success = successes[0]
    assert success["active"] is False
    assert success["revoked_by"] == 777

    # All others should be None
    for r in results:
        if r is not success:
            assert r is None

    # Final stored data must reflect inactive penalty
    all_p = svc.get_all()
    assert len(all_p) == 1
    stored = all_p[0]
    assert stored["penalty_id"] == pid
    assert stored["active"] is False
    assert stored["revoked_by"] == 777

