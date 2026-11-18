"""Numbers and text for the Dashboard and Live Tracker pages. No Qt, so it is unit-tested."""
from __future__ import annotations

import time

from app.overlay.model import format_timer

DETECTION_BANNER = ("Counting is manual for now. Automatic chest detection arrives in v1.1.9 "
                    "and needs your recorded samples.")


def overall_stats(db, counter) -> dict:
    """Saved history + the match in progress (an empty live match is not counted as a match,
    the same rule used when matches are stored)."""
    live = counter.match_count
    matches = db.total_matches() + (1 if live > 0 else 0)
    total = db.total_chests() + live
    return {
        "match": live,
        "session": counter.session_count,
        "total": total,
        "matches": matches,
        "average": round(total / matches, 1) if matches else 0.0,
        "best": max(db.personal_best(), live),
    }


def stat_cards(stats: dict) -> list[tuple[str, str]]:
    """(label, value) pairs in display order."""
    return [
        ("This match", str(stats["match"])),
        ("This session", str(stats["session"])),
        ("Total chests", str(stats["total"])),
        ("Matches", str(stats["matches"])),
        ("Average / match", f"{stats['average']:.1f}"),
        ("Personal best", str(stats["best"])),
    ]


def format_clock(ts: float) -> str:
    return time.strftime("%H:%M:%S", time.localtime(ts))


def format_event(ev) -> str:
    if ev.source == "manual":
        what = "added (manual)" if ev.delta > 0 else "removed (manual)"
    else:
        what = f"detected ({round(ev.confidence * 100)}%)"
    sign = "+1" if ev.delta > 0 else "-1"
    return f"{format_clock(ev.timestamp)}   {sign}   {what}"


def recent_event_lines(events, limit: int = 30) -> list[str]:
    """Newest first."""
    return [format_event(e) for e in reversed(events[-limit:])]


def format_match_row(row) -> tuple[str, str, str]:
    """(date, duration, chests) for the match history table."""
    date = time.strftime("%d %b %H:%M", time.localtime(row["started_at"]))
    return date, format_timer(row["duration_s"] or 0), str(row["chests"])
