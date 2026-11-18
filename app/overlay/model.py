"""Display logic for the overlay. No Qt in here, so it is unit-tested."""
from __future__ import annotations

BASE_W, BASE_H = 260, 124

STATUS_MANUAL = "MANUAL MODE"   # no detector exists yet (arrives in a later version)
STATUS_WATCHING = "WATCHING"
STATUS_PAUSED = "PAUSED"
STATUS_ERROR = "ERROR"


def format_timer(seconds: float) -> str:
    s = max(0, int(seconds))
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m:02d}:{sec:02d}"


def scaled_size(scale: float) -> tuple[int, int]:
    scale = min(3.0, max(0.5, scale))
    return round(BASE_W * scale), round(BASE_H * scale)


def clamp_position(x: int, y: int, w: int, h: int, screen_w: int, screen_h: int) -> tuple[int, int]:
    """Keep the overlay fully on screen (e.g. after a monitor change)."""
    return (max(0, min(x, max(0, screen_w - w))),
            max(0, min(y, max(0, screen_h - h))))


def snapshot(counter, status: str = STATUS_MANUAL) -> dict:
    """Everything the overlay draws, taken from a ChestCounter."""
    return {
        "match": counter.match_count,
        "session": counter.session_count,
        "timer": format_timer(counter.match_elapsed()),
        "status": status,
    }
