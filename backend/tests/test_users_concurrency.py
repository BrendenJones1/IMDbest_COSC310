# backend/tests/test_users_concurrency.py

from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi import HTTPException, status

from backend.repositories.users_repo import UserRepository
from backend.services.users_service import UserService
from schemas.user import UserCreate


@pytest.fixture
def user_service_tmp(tmp_path):
    """
    Fresh UserService backed by a temp users.json for each test.
    """
    users_file = tmp_path / "users.json"
    repo = UserRepository(users_file)
    # start from an empty list of users
    repo.save_users([])
    return UserService(user_repo=repo)


# ---------------------------------
# P1: Multiple reads only
# ---------------------------------

def test_concurrent_reads_user_list_only(user_service_tmp):
    """
    P1: Concurrent read-only operations.

    Seed a few users, then hammer list_users + get_user_by_username
    from multiple threads. Expect:
      - no exceptions
      - all readers see a consistent snapshot
    """
    service = user_service_tmp

    names = ["alice", "bob", "carol"]
    for name in names:
        service.register(UserCreate(
            username=name,
            email=f"{name}@example.com",
            password="secret123",
        ))

    def reader():
        users = service.list_users()
        usernames = {u.username for u in users}
        assert usernames == set(names)

        # also exercise get_user_by_username inside the same reader
        for name in names:
            u = service.get_user_by_username(name)
            assert u.username == name

    with ThreadPoolExecutor(max_workers=10) as pool:
        list(pool.map(lambda _: reader(), range(20)))


# ---------------------------------
# P2a: Concurrent writes (register)
# ---------------------------------

def test_concurrent_register_unique_users_no_loss(user_service_tmp):
    """
    P2a: Many concurrent register() calls with distinct usernames/emails.

    Expect:
      - no JSON corruption
      - number of stored users == number of attempted registrations
      - all usernames present
      - IDs are unique
      - exactly one admin, rest user (based on your register logic)
    """
    service = user_service_tmp

    usernames = [f"user{i}" for i in range(20)]

    def worker(name: str):
        payload = UserCreate(
            username=name,
            email=f"{name}@example.com",
            password="pw123456",
        )
        return service.register(payload)

    with ThreadPoolExecutor(max_workers=8) as pool:
        _results = list(pool.map(worker, usernames))

    users = service.user_repo.load_users() or []

    # No lost writes
    assert len(users) == len(usernames)
    stored_names = {u["username"] for u in users}
    assert stored_names == set(usernames)

    # IDs unique
    assert len({u["id"] for u in users}) == len(users)

    # Exactly one admin, rest users
    num_admins = sum(1 for u in users if u["role"] == "admin")
    assert num_admins == 1
    assert {u["role"] for u in users} == {"admin", "user"}


def test_concurrent_register_same_username_enforces_uniqueness(user_service_tmp):
    """
    P2a variant: All threads race to register the SAME username.

    Pre-create 'alice', then concurrently attempt to register 'alice' again
    with different emails. Expect:
      - still only one 'alice' in storage
      - additional attempts either fail with 409 or (at most) one extra success
        if interleaving is weird, but never duplicate persisted usernames.
    """
    service = user_service_tmp

    # Baseline user
    service.register(UserCreate(
        username="alice",
        email="alice@example.com",
        password="secret123",
    ))

    def worker(i: int):
        payload = UserCreate(
            username="alice",
            email=f"alice+{i}@example.com",
            password="secret123",
        )
        try:
            service.register(payload)
            return "ok"
        except HTTPException as exc:
            return exc.status_code

    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(worker, range(10)))

    users = service.user_repo.load_users() or []
    alices = [u for u in users if u["username"] == "alice"]
    # Only one 'alice' persisted
    assert len(alices) == 1

    # Most/all concurrent attempts should fail with 409
    for r in results:
        assert r in ("ok", status.HTTP_409_CONFLICT)

    # At most one extra "ok" (ideally none) from the race;
    # but the stored data still has only one alice.
    assert sum(1 for r in results if r == "ok") <= 1


# ---------------------------------
# P2b: Concurrent promote_user on same target
# ---------------------------------

def test_concurrent_promote_user_only_once(user_service_tmp):
    """
    P2b: Many threads attempt to promote the same user concurrently.

    Expect:
      - exactly one successful promotion (returns role 'admin')
      - all other threads get HTTP 400 'User already an admin'
      - final stored role is 'admin' with no corruption
    """
    service = user_service_tmp

    # Create several users; first will be admin, others normal users
    ids = []
    for i in range(3):
        res = service.register(UserCreate(
            username=f"userp{i}",
            email=f"userp{i}@example.com",
            password="pw",
        ))
        ids.append(res["user"].id)

    target_id = ids[1]  # this one should start as role 'user'

    def worker():
        try:
            result = service.promote_user(target_id)
            # on success, promote_user returns the user dict
            return result.get("role")
        except HTTPException as exc:
            return exc.status_code

    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(lambda _: worker(), range(5)))

    # Check final stored role
    users = service.user_repo.load_users() or []
    target = next(u for u in users if u["id"] == target_id)
    assert target["role"] == "admin"

    # Exactly one success ('admin'), others 400
    assert results.count("admin") == 1
    for r in results:
        if r != "admin":
            assert r == status.HTTP_400_BAD_REQUEST
