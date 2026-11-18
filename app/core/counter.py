"""Chest counter: the single source of truth for counts.

Pure logic (no GUI, no capture) so it can be unit-tested without Fortnite.
Detectors feed it candidate events; it enforces confidence threshold and cooldown.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ChestEvent:
    timestamp: float          # wall-clock (time.time) for display/storage
    confidence: float
    source: str               # "vision" | "manual"
    delta: int = 1            # +1 detection, +/-1 manual


class ChestCounter:
    def __init__(self, sensitivity: float = 0.80, cooldown_s: float = 1.5,
                 clock: Callable[[], float] = time.monotonic,
                 wallclock: Callable[[], float] = time.time):
        self.sensitivity = sensitivity
        self.cooldown_s = cooldown_s
        self._clock = clock
        self._wall = wallclock
        self.match_count = 0
        self.session_count = 0
        self.events: list[ChestEvent] = []
        self._last_accept: float | None = None
        self.match_started_at = self._wall()
        self._match_t0 = self._clock()

    # ---- detection input -------------------------------------------------
    def register_detection(self, confidence: float, source: str = "vision") -> bool:
        """Return True if counted. Rejects low confidence and duplicates in cooldown."""
        if confidence < self.sensitivity:
            return False
        now = self._clock()
        if self._last_accept is not None and (now - self._last_accept) < self.cooldown_s:
            return False
        self._last_accept = now
        self.match_count += 1
        self.session_count += 1
        self.events.append(ChestEvent(self._wall(), confidence, source, +1))
        return True

    # ---- manual correction ----------------------------------------------
    def manual_adjust(self, delta: int) -> None:
        if delta not in (-1, 1):
            raise ValueError("manual adjustment must be +1 or -1")
        if delta < 0 and self.match_count == 0:
            return  # never go negative
        self.match_count += delta
        self.session_count = max(0, self.session_count + delta)
        self.events.append(ChestEvent(self._wall(), 1.0, "manual", delta))

    # ---- match lifecycle -------------------------------------------------
    def match_elapsed(self) -> float:
        return self._clock() - self._match_t0

    def new_match(self) -> dict:
        """Finish the current match, return its summary, reset match state."""
        summary = {
            "started_at": self.match_started_at,
            "ended_at": self._wall(),
            "duration_s": self.match_elapsed(),
            "chests": self.match_count,
            "events": list(self.events),
        }
        self.match_count = 0
        self.events = []
        self._last_accept = None
        self.match_started_at = self._wall()
        self._match_t0 = self._clock()
        return summary
