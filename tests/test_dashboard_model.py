import re

from app.core.counter import ChestCounter, ChestEvent
from app.database.db import Database
from app.ui.dashboard_model import (format_event, format_match_row, overall_stats,
                                    recent_event_lines, stat_cards)


def counter_with(n):
    c = ChestCounter(0.8, 1.0)
    for _ in range(n):
        c.manual_adjust(1)
    return c


def test_stats_empty():
    db = Database(":memory:")
    s = overall_stats(db, counter_with(0))
    assert s == {"match": 0, "session": 0, "total": 0, "matches": 0, "average": 0.0, "best": 0}


def test_stats_combine_saved_and_live():
    db = Database(":memory:")
    c = counter_with(4)
    db.save_match(c.new_match())                 # saved: 4
    c.manual_adjust(1); c.manual_adjust(1)       # live: 2
    s = overall_stats(db, c)
    assert (s["total"], s["matches"], s["best"], s["match"], s["session"]) == (6, 2, 4, 2, 6)
    assert s["average"] == 3.0
    assert overall_stats(db, counter_with(9))["best"] == 9    # live beats saved best


def test_stat_cards_order_and_text():
    cards = stat_cards({"match": 1, "session": 2, "total": 3, "matches": 4, "average": 0.75, "best": 5})
    assert [l for l, _ in cards] == ["This match", "This session", "Total chests",
                                     "Matches", "Average / match", "Personal best"]
    assert dict(cards)["Average / match"] == "0.8"      # one decimal


def test_event_text():
    m = ChestEvent(0.0, 1.0, "manual", +1)
    r = ChestEvent(0.0, 1.0, "manual", -1)
    v = ChestEvent(0.0, 0.954, "vision", +1)
    assert re.fullmatch(r"\d\d:\d\d:\d\d   \+1   added \(manual\)", format_event(m))
    assert format_event(r).endswith("-1   removed (manual)")
    assert format_event(v).endswith("+1   detected (95%)")


def test_recent_events_newest_first_and_limited():
    evs = [ChestEvent(float(i), 1.0, "manual", 1) for i in range(50)]
    lines = recent_event_lines(evs, limit=3)
    assert len(lines) == 3
    assert lines == [format_event(evs[49]), format_event(evs[48]), format_event(evs[47])]


def test_match_row():
    db = Database(":memory:")
    c = counter_with(3)
    db.save_match({"started_at": 1_700_000_000.0, "ended_at": 1_700_000_725.0,
                   "duration_s": 725.0, "chests": 3, "events": []})
    date, dur, n = format_match_row(db.recent_matches(1)[0])
    assert re.fullmatch(r"\d\d \w{3} \d\d:\d\d", date)
    assert (dur, n) == ("12:05", "3")
