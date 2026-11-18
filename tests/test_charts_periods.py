from datetime import datetime

from app.core.counter import ChestCounter
from app.database.db import Database
from app.ui.dashboard_model import bar_fractions, chart_values, day_start, overall_stats

NOON = datetime(2026, 11, 18, 12, 0).timestamp()


def at(day, hour=12):
    return datetime(2026, 11, day, hour, 0).timestamp()


def match(started, chests):
    return {"started_at": started, "ended_at": started + 60, "duration_s": 60.0, "chests": chests, "events": []}


def live(n):
    c = ChestCounter(0.8, 1.0)
    for _ in range(n):
        c.manual_adjust(1)
    return c


def test_day_start_is_local_midnight():
    assert day_start(NOON) == datetime(2026, 11, 18, 0, 0).timestamp()
    assert day_start(NOON, 6) == datetime(2026, 11, 12, 0, 0).timestamp()


def test_today_and_week_totals():
    db = Database(":memory:")
    db.save_match(match(at(18, 9), 5))      # today
    db.save_match(match(at(17), 3))         # yesterday
    db.save_match(match(at(12, 0), 2))      # 6 days back, just inside
    db.save_match(match(at(11, 23), 40))    # 7 days back: outside the window
    s = overall_stats(db, live(0), now=NOON)
    assert (s["today"], s["week"]) == (5, 10)
    assert s["total"] == 50                 # all-time is unchanged


def test_live_match_counts_as_today():
    db = Database(":memory:")
    db.save_match(match(at(10), 4))         # old match
    s = overall_stats(db, live(3), now=NOON)
    assert (s["today"], s["week"]) == (3, 3)


def test_chart_values_oldest_first_with_live_last_and_limited():
    db = Database(":memory:")
    for i in range(1, 26):
        db.save_match(match(1000.0 + i, i))
    vals = chart_values(db, live(0), limit=20)
    assert vals == list(range(6, 26))
    assert chart_values(db, live(2), limit=20) == list(range(7, 26)) + [2]
    assert chart_values(Database(":memory:"), live(0)) == []


def test_bar_fractions():
    assert bar_fractions([2, 4, 0]) == [0.5, 1.0, 0.0]
    assert bar_fractions([0, 0]) == [0.0, 0.0]
    assert bar_fractions([]) == []
