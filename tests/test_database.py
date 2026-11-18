import csv
from app.core.counter import ChestCounter
from app.database.db import Database


def finished_match(n):
    t = [0.0]
    c = ChestCounter(0.8, 1.0, clock=lambda: t[0])
    for _ in range(n):
        c.register_detection(0.9); t[0] += 2
    return c.new_match()


def test_save_and_stats(tmp_path):
    db = Database(tmp_path / "x.db")
    sid = db.start_session(1.0)
    db.save_match(finished_match(3), sid)
    db.save_match(finished_match(7), sid)
    assert db.total_chests() == 10
    assert db.total_matches() == 2
    assert db.average_per_match() == 5.0
    assert db.personal_best() == 7
    db.close()


def test_persistence_across_reopen(tmp_path):
    p = tmp_path / "x.db"
    db = Database(p); db.save_match(finished_match(4)); db.close()
    assert Database(p).total_chests() == 4


def test_csv_export(tmp_path):
    db = Database(tmp_path / "x.db")
    db.save_match(finished_match(2))
    out = tmp_path / "o.csv"
    assert db.export_matches_csv(out) == 1
    rows = list(csv.reader(open(out, encoding="utf-8")))
    assert rows[0][-1] == "chests" and rows[1][-1] == "2"


def test_reset(tmp_path):
    db = Database(tmp_path / "x.db")
    db.save_match(finished_match(2)); db.reset_statistics()
    assert db.total_matches() == 0
