# tests/test_flags_concurrency.py
import json
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time

import pytest

from backend.services.flags_service import FlagsService


def _read_file(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_concurrent_add_flags_unique_ids(tmp_path):
    """
    Spawn many concurrent add_flag calls and assert that:
      - the final number of flags equals the number of adds
      - each flag_id is unique (no duplicates)
    NOTE: If this test fails, it indicates a read-modify-write race in FlagsService (expected
    if service does not use a transaction/lock across load+save).
    """
    file_path = tmp_path / "flags.json"
    svc = FlagsService(path=str(file_path))

    adds = 200
    # small helper to randomize interleaving
    def add_one(i):
        # slight jitter to increase chance of race
        time.sleep(random.uniform(0, 0.01))
        return svc.add_flag(review_id=i, flagger_id=100 + i, flagged_user_id=200 + i, reason=f"r{i}")

    with ThreadPoolExecutor(max_workers=20) as ex:
        futures = [ex.submit(add_one, i) for i in range(adds)]
        results = [f.result() for f in as_completed(futures)]

    # verify file length
    data = _read_file(file_path)
    assert len(data) == adds, f"expected {adds} flags, got {len(data)}"

    # verify IDs are unique
    ids = [f["flag_id"] for f in data]
    assert len(ids) == len(set(ids)), f"duplicate flag_id detected: {ids}"

    # optional: verify continuous 1..N (not strictly required, but useful)
    assert set(ids) == set(range(1, adds + 1)), "flag_id set does not match expected 1..N"


def test_concurrent_update_flag_status(tmp_path):
    """
    Create a bunch of flags, then concurrently update their statuses.
    This ensures updates persist and do not clobber each other.
    """
    file_path = tmp_path / "flags.json"
    svc = FlagsService(path=str(file_path))

    total = 100
    # create flags sequentially to have stable ids
    for i in range(total):
        svc.add_flag(review_id=i, flagger_id=i, flagged_user_id=100 + i, reason="initial")

    # choose half to set to 'resolved' concurrently, half to 'rejected'
    ids = list(range(1, total + 1))
    random.shuffle(ids)
    half = total // 2
    to_resolve = ids[:half]
    to_reject = ids[half:]

    def set_status(fid, status):
        # jitter to increase interleaving
        time.sleep(random.uniform(0, 0.01))
        return svc.update_flag_status(fid, status)

    tasks = []
    with ThreadPoolExecutor(max_workers=30) as ex:
        for fid in to_resolve:
            tasks.append(ex.submit(set_status, fid, "resolved"))
        for fid in to_reject:
            tasks.append(ex.submit(set_status, fid, "rejected"))

        # collect results
        results = [t.result() for t in as_completed(tasks)]

    # load and check consistency
    data = svc.get_all_flags()
    id_to_status = {f["flag_id"]: f["status"] for f in data}
    for fid in to_resolve:
        assert id_to_status[fid] == "resolved", f"flag {fid} expected 'resolved' got {id_to_status[fid]}"
    for fid in to_reject:
        assert id_to_status[fid] == "rejected", f"flag {fid} expected 'rejected' got {id_to_status[fid]}"


def test_no_temp_file_left_after_save(tmp_path):
    """
    Ensure that .tmp file is not left behind after concurrent saves.
    Repository.write uses atomic os.replace(tmp, target) under lock;
    this test runs concurrent add operations and finally asserts there are no .tmp leftovers.
    """
    file_path = tmp_path / "flags.json"
    svc = FlagsService(path=str(file_path))

    # perform concurrent adds
    adds = 50

    def add(i):
        time.sleep(random.uniform(0, 0.005))
        svc.add_flag(review_id=i, flagger_id=i, flagged_user_id=100 + i, reason="tmp-check")
        return i

    with ThreadPoolExecutor(max_workers=10) as ex:
        list(ex.map(add, range(adds)))

    # assert .tmp files are not present
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert tmp_files == [], f"found leftover temp files: {tmp_files}"

    # ensure final file is valid json
    data = _read_file(file_path)
    assert isinstance(data, list), "final file malformed (not a list)"
