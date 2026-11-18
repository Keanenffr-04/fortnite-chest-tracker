"""Numbers and text for the Dashboard and Live Tracker pages. No Qt, so it is unit-tested."""
from __future__ import annotations

import time
from datetime import date, datetime, time as dtime, timedelta

from app.overlay.model import format_timer

DETECTION_BANNER = ("Counting is manual for now: press +1 on the Live Tracker, in the overlay menu, "
                    "or use your hotkeys. Automatic counting comes in a later version.")


def day_start(now: float, days_back: int = 0) -> float:
    """Local midnight, days_back days before the day that contains `now`."""
    d = datetime.fromtimestamp(now).date() - timedelta(days=days_back)
    return datetime.combine(d, dtime.min).timestamp()


def day_bounds(d: date) -> tuple[float, float]:
    """Local midnight of `d` and of the next day."""
    return (datetime.combine(d, dtime.min).timestamp(),
            datetime.combine(d + timedelta(days=1), dtime.min).timestamp())


def day_totals(db, counter, d: date, now: float | None = None) -> tuple[int, int]:
    """(chests, matches) for local day `d`. The match in progress counts as today (only if it has chests,
    the same rule used when matches are stored)."""
    now = time.time() if now is None else now
    chests, matches = db.totals_between(*day_bounds(d))
    if d == datetime.fromtimestamp(now).date() and counter.match_count > 0:
        chests += counter.match_count
        matches += 1
    return chests, matches


def day_title(d: date, today: date) -> str:
    """'Today', 'Yesterday' or e.g. 'Mon 16 Nov 2026'."""
    if d == today:
        return "Today"
    if d == today - timedelta(days=1):
        return "Yesterday"
    return d.strftime("%a %d %b %Y")


def days_back_for(picked: date, today: date) -> int:
    """How many days before `today` a calendar pick is. Future dates count as today (never negative)."""
    return max(0, (today - picked).days)


def day_summary(chests: int, matches: int) -> str:
    if not matches:
        return "No matches on this day"
    return f"{matches} match{'es' if matches != 1 else ''}"


def chart_values(db, counter, limit: int = 20) -> list[int]:
    """Chests per match, oldest -> newest, ending with the match in progress (if it has chests)."""
    vals = [r["chests"] for r in reversed(db.recent_matches(limit))]
    if counter.match_count > 0:
        vals.append(counter.match_count)
    return vals[-limit:]


def daily_values(db, counter, days: int = 14, now: float | None = None) -> list[int]:
    """Chests per local day, oldest -> newest, ending with today (the match in progress counts as today)."""
    now = time.time() if now is None else now
    first = day_start(now, days - 1)
    vals = [0] * days
    for r in db.matches_since(first):
        idx = (datetime.fromtimestamp(r["started_at"]).date() - datetime.fromtimestamp(first).date()).days
        if 0 <= idx < days:
            vals[idx] += r["chests"]
    vals[-1] += counter.match_count
    return vals


def best_flags(rows) -> list[bool]:
    """True for every match that equals the personal best (ties all count; a best of 0 is not a highlight)."""
    best = max((r["chests"] for r in rows), default=0)
    return [best > 0 and r["chests"] == best for r in rows]


def chests_label(chests: str, is_best: bool) -> str:
    return f"\u2605 {chests}" if is_best else chests


def bar_fractions(values: list[int]) -> list[float]:
    """Bar heights as 0..1 of the tallest bar (an all-zero list gives all zeros)."""
    top = max(values, default=0)
    return [v / top if top else 0.0 for v in values]


def overall_stats(db, counter, now: float | None = None) -> dict:
    """Saved history + the match in progress (an empty live match is not counted as a match,
    the same rule used when matches are stored)."""
    live = counter.match_count
    matches = db.total_matches() + (1 if live > 0 else 0)
    total = db.total_chests() + live
    now = time.time() if now is None else now
    return {
        "match": live,
        "session": counter.session_count,
        "total": total,
        "matches": matches,
        "average": round(total / matches, 1) if matches else 0.0,
        "best": max(db.personal_best(), live),
        # the match in progress counts as today (it is being played now)
        "today": db.chests_since(day_start(now)) + live,
        "week": db.chests_since(day_start(now, 6)) + live,      # today + the 6 days before
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
        ("Today", str(stats["today"])),
        ("Last 7 days", str(stats["week"])),
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


def export_filename(ts: float) -> str:
    """Suggested name for the CSV export, e.g. chest_matches_2026-11-18.csv"""
    return time.strftime("chest_matches_%Y-%m-%d.csv", time.localtime(ts))


def history_summary(rows) -> str:
    """One line above the History table."""
    n = len(rows)
    if not n:
        return "No finished matches yet."
    total = sum(r["chests"] for r in rows)
    return f"{n} match{'es' if n != 1 else ''}, {total} chest{'s' if total != 1 else ''} in total"


def format_match_row(row) -> tuple[str, str, str]:
    """(date, duration, chests) for the match history table."""
    date = time.strftime("%d %b %H:%M", time.localtime(row["started_at"]))
    return date, format_timer(row["duration_s"] or 0), str(row["chests"])
