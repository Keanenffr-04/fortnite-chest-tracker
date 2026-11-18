from datetime import date, datetime

from app.core.counter import ChestCounter
from app.database.db import Database
from app.ui.dashboard_model import day_bounds, day_summary, day_title, day_totals

NOON = datetime(2026, 11, 18, 12, 0).timestamp()
TODAY = date(2026, 11, 18)


def at(day, hour=12):
    return datetime(2026, 11, day, hour, 0).timestamp()


def match(started, chests):
    return {"started_at": started, "ended_at": started + 60, "duration_s": 60.0, "chests": chests, "events": []}


def live(n):
    c = ChestCounter(0.8, 1.0)
    for _ in range(n):
        c.manual_adjust(1)
    return c


def test_day_bounds_cover_one_local_day():
    a, b = day_bounds(TODAY)
    assert a == datetime(2026, 11, 18, 0, 0).timestamp() and b == datetime(2026, 11, 19, 0, 0).timestamp()


def test_totals_between_is_half_open():
    db = Database(":memory:")
    a, b = day_bounds(TODAY)
    db.save_match(match(a, 2))              # exactly midnight: inside
    db.save_match(match(b, 9))              # next midnight: outside
    assert db.totals_between(a, b) == (2, 1)


def test_day_totals_pick_the_right_day():
    db = Database(":memory:")
    db.save_match(match(at(17, 23), 4)); db.save_match(match(at(17, 1), 1))
    db.save_match(match(at(18, 9), 6))
    assert day_totals(db, live(0), date(2026, 11, 17), now=NOON) == (5, 2)
    assert day_totals(db, live(0), TODAY, now=NOON) == (6, 1)
    assert day_totals(db, live(0), date(2026, 11, 10), now=NOON) == (0, 0)


def test_live_match_only_counts_on_today():
    db = Database(":memory:")
    assert day_totals(db, live(3), TODAY, now=NOON) == (3, 1)
    assert day_totals(db, live(3), date(2026, 11, 17), now=NOON) == (0, 0)
    assert day_totals(db, live(0), TODAY, now=NOON) == (0, 0)      # empty live match is not a match


def test_day_title_and_summary():
    assert day_title(TODAY, TODAY) == "Today"
    assert day_title(date(2026, 11, 17), TODAY) == "Yesterday"
    assert day_title(date(2026, 11, 16), TODAY) == "Mon 16 Nov 2026"
    assert day_summary(0, 0) == "No matches on this day"
    assert day_summary(5, 1) == "1 match" and day_summary(9, 3) == "3 matches"
