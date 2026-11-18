"""TrackerController: the one object the overlay AND the main window both talk to.

Owns settings, counter, database, session and sound. No Qt in here (unit-tested).
Listeners are called as listener(kind) with kind one of:
  "tick"      - once a second (timer text changed)
  "count"     - a chest was added / removed
  "match"     - a match was finished and a new one started
  "settings"  - a setting changed (apply_changes, overlay menu, hotkey toggles, reset)
  "stream"    - the overlay was shown / hidden (Start stream button, hotkey, overlay menu)
  "reset"     - saved statistics were deleted
"""
from __future__ import annotations

import time
from dataclasses import fields
from pathlib import Path
from typing import Callable

from app.config.settings import Settings
from app.core import startup
from app.core.counter import ChestCounter
from app.overlay.model import STATUS_MANUAL, apply_option
from app.ui.dashboard_model import overall_stats
from app.ui.settings_model import apply_changes, defaults_keeping


class TrackerController:
    def __init__(self, settings: Settings, db, sound, settings_path: Path | None = None,
                 startup_setter: Callable[[bool], str | None] = startup.set_enabled,
                 overlay_visible: bool = True):
        self.settings = settings
        self.db = db
        self.sound = sound
        self.settings_path = settings_path
        self._startup_setter = startup_setter
        # Whether the overlay (the small box) is showing. NOT saved: the main window starts with it
        # hidden and you press Start stream to show it.
        self.overlay_visible = bool(overlay_visible)
        self.status = STATUS_MANUAL      # a detector (v1.1.9) will change this
        self.counter = ChestCounter(settings.detection_sensitivity, settings.detection_cooldown_s)
        self.session_id = db.start_session(time.time())
        self._listeners: list[Callable[[str], None]] = []

    # ---- listeners -------------------------------------------------------
    def subscribe(self, fn: Callable[[str], None]) -> None:
        self._listeners.append(fn)

    def notify(self, kind: str) -> None:
        for fn in list(self._listeners):
            try:
                fn(kind)
            except Exception as e:      # a broken UI listener must never break counting
                print(f"UI listener error ({kind}): {e}")

    def tick(self) -> None:
        self.notify("tick")

    # ---- counting --------------------------------------------------------
    def add(self) -> None:
        self.counter.manual_adjust(1)
        self.sound.play_up()
        self.notify("count")

    def remove(self) -> None:
        had_chest = self.counter.match_count > 0
        self.counter.manual_adjust(-1)
        if had_chest:
            self.sound.play_down()
        self.notify("count")

    def new_match(self) -> int | None:
        """Finish the current match. Returns the saved match id (None if it had no chests)."""
        mid = self._store_match()
        self.notify("match")
        return mid

    def _store_match(self) -> int | None:
        summary = self.counter.new_match()
        if summary["chests"] > 0:        # don't store empty matches
            return self.db.save_match(summary, self.session_id)
        return None

    def recent_events(self):
        return list(self.counter.events)

    def stats(self) -> dict:
        return overall_stats(self.db, self.counter)

    # ---- settings --------------------------------------------------------
    def _save(self) -> None:
        self.settings.save(self.settings_path)

    def _adopt(self, new: Settings) -> None:
        """Copy values into the SAME settings object so everyone holding it stays in sync."""
        for f in fields(Settings):
            setattr(self.settings, f.name, getattr(new, f.name))
        self.counter.sensitivity = self.settings.detection_sensitivity
        self.counter.cooldown_s = self.settings.detection_cooldown_s
        self.sound.update(self.settings.sound_enabled, self.settings.sound_volume)

    def set_option(self, key: str, value) -> None:
        """One overlay option from the right-click menu."""
        try:
            apply_option(self.settings, key, value)
        except ValueError as e:
            print(f"Ignored option change: {e}")
            return
        self._adopt(self.settings)
        self._save()
        self.notify("settings")

    def apply_changes(self, changes: dict) -> tuple[list[str], list[str]]:
        """Apply Settings-page changes all-or-nothing. Returns (problems, warnings).
        If problems is non-empty nothing was changed."""
        new, problems = apply_changes(self.settings, changes)
        if problems:
            return problems, []
        warnings: list[str] = []
        if new.start_with_windows != self.settings.start_with_windows:
            err = self._startup_setter(new.start_with_windows)
            if err:
                new.start_with_windows = self.settings.start_with_windows   # keep the truth
                warnings.append(err)
        self._adopt(new)
        self._save()
        self.notify("settings")
        return [], warnings

    def reset_settings(self) -> list[str]:
        """Back to factory settings (keeps data folder + overlay position). Returns warnings."""
        warnings: list[str] = []
        fresh = defaults_keeping(self.settings)
        if self.settings.start_with_windows:
            err = self._startup_setter(False)
            if err:
                warnings.append(err)
        self._adopt(fresh)
        self._save()
        self.notify("settings")
        return warnings

    def set_overlay_visible(self, visible: bool) -> None:
        self.overlay_visible = bool(visible)
        self.notify("stream")

    def set_click_through(self, on: bool) -> None:
        self.settings.overlay_click_through = bool(on)
        self._save()
        self.notify("settings")

    def set_overlay_position(self, x: int, y: int) -> None:
        self.settings.overlay_x, self.settings.overlay_y = int(x), int(y)
        self._save()          # no notify: the window is already where the user dropped it

    # ---- data ------------------------------------------------------------
    def reset_statistics(self) -> None:
        """Delete all saved matches/events. The match in progress is kept."""
        self.db.reset_statistics()
        self.session_id = self.db.start_session(time.time())
        self.notify("reset")

    def finish(self) -> None:
        """App is closing: save the match in progress and close the session + database."""
        self._store_match()
        self.db.end_session(self.session_id, time.time())
        self.db.close()
