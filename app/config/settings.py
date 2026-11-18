"""Persistent user settings stored as JSON (no personal data, no secrets)."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

from app import APP_NAME


THEME_NAMES = ("violet", "blue", "green", "red")


def app_data_dir() -> Path:
    """%APPDATA%\\FortniteChestTracker on Windows, ~/.fortnitechesttracker elsewhere."""
    base = os.environ.get("APPDATA")
    path = Path(base) / APP_NAME if base else Path.home() / ".fortnitechesttracker"
    path.mkdir(parents=True, exist_ok=True)
    return path


@dataclass
class Settings:
    # Detection
    detection_sensitivity: float = 0.80   # min confidence 0.0-1.0 to accept
    detection_cooldown_s: float = 1.5     # ignore repeat detections inside this window
    detection_interval_ms: int = 100      # capture/scan interval (10 fps default)
    sound_enabled: bool = True
    sound_volume: float = 0.5
    # Capture / recording (v1.1.2)
    capture_monitor: int = 1              # 1 = primary monitor
    record_pre_s: float = 5.0             # seconds of footage kept BEFORE you press the mark key
    record_post_s: float = 3.0            # seconds saved AFTER
    hotkey_mark_chest: str = "f8"         # "a chest just opened"
    hotkey_mark_negative: str = "f9"      # "nothing special" (helps cut false positives)
    hotkey_stop_recording: str = "f10"
    # Overlay
    overlay_opacity: float = 0.85
    overlay_x: int = 20
    overlay_y: int = 20
    overlay_scale: float = 1.0
    overlay_click_through: bool = False
    overlay_visible: bool = True
    overlay_theme: str = "violet"
    overlay_show_session: bool = True
    overlay_show_timer: bool = True
    overlay_show_status: bool = True
    # Hotkeys
    hotkey_toggle_overlay: str = "ctrl+shift+o"
    hotkey_add_chest: str = "ctrl+shift+up"
    hotkey_remove_chest: str = "ctrl+shift+down"
    hotkey_toggle_click_through: str = "ctrl+shift+c"
    hotkey_quit: str = "ctrl+shift+q"
    # App
    start_with_windows: bool = False
    data_dir: str = field(default_factory=lambda: str(app_data_dir()))

    def validate(self) -> None:
        self.detection_sensitivity = min(1.0, max(0.0, float(self.detection_sensitivity)))
        self.detection_cooldown_s = max(0.0, float(self.detection_cooldown_s))
        self.detection_interval_ms = max(20, int(self.detection_interval_ms))
        self.sound_volume = min(1.0, max(0.0, float(self.sound_volume)))
        if self.overlay_theme not in THEME_NAMES:
            self.overlay_theme = "violet"
        self.capture_monitor = max(1, int(self.capture_monitor))
        self.record_pre_s = min(15.0, max(1.0, float(self.record_pre_s)))
        self.record_post_s = min(15.0, max(0.5, float(self.record_post_s)))
        self.overlay_opacity = min(1.0, max(0.1, float(self.overlay_opacity)))
        self.overlay_scale = min(3.0, max(0.5, float(self.overlay_scale)))

    @classmethod
    def load(cls, path: Path | None = None) -> "Settings":
        path = path or app_data_dir() / "settings.json"
        s = cls()
        try:
            raw = json.loads(Path(path).read_text(encoding="utf-8"))
            known = {f.name for f in fields(cls)}
            for k, v in raw.items():
                if k in known:
                    setattr(s, k, v)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass  # fall back to defaults; never crash on a bad settings file
        s.validate()
        return s

    def save(self, path: Path | None = None) -> None:
        path = Path(path or app_data_dir() / "settings.json")
        self.validate()
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        tmp.replace(path)  # atomic-ish write so a crash can't corrupt settings
