"""Display logic for the overlay. No Qt in here, so it is unit-tested."""
from __future__ import annotations

BASE_W, BASE_H = 260, 124
BASE_H_NO_FOOTER = 92       # height when both Session and Timer are hidden

STATUS_MANUAL = "MANUAL MODE"   # no detector exists yet (arrives in a later version)
STATUS_WATCHING = "WATCHING"
STATUS_PAUSED = "PAUSED"
STATUS_ERROR = "ERROR"

# name -> (accent 1 RGB, accent 2 RGB). Default "violet" = purple + blue.
THEMES = {
    "violet": ((168, 85, 247), (59, 130, 246)),
    "blue": ((59, 130, 246), (34, 211, 238)),
    "green": ((34, 197, 94), (20, 184, 166)),
    "red": ((239, 68, 68), (249, 115, 22)),
    "pirate": ((245, 197, 66), (194, 120, 34)),      # gold coin + copper (v1.1.15)
}
OPACITY_PRESETS = [0.4, 0.6, 0.8, 1.0]
SIZE_PRESETS = {"Small": 0.8, "Normal": 1.0, "Large": 1.3, "Extra large": 1.6}

# option key (used by the right-click menu) -> Settings attribute
OPTION_ATTRS = {
    "opacity": "overlay_opacity",
    "scale": "overlay_scale",
    "theme": "overlay_theme",
    "show_session": "overlay_show_session",
    "show_timer": "overlay_show_timer",
    "show_status": "overlay_show_status",
    "sound_enabled": "sound_enabled",
}


def format_timer(seconds: float) -> str:
    s = max(0, int(seconds))
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m:02d}:{sec:02d}"


def scaled_size(scale: float, footer: bool = True) -> tuple[int, int]:
    scale = min(3.0, max(0.5, scale))
    base_h = BASE_H if footer else BASE_H_NO_FOOTER
    return round(BASE_W * scale), round(base_h * scale)


def clamp_position(x: int, y: int, w: int, h: int, screen_w: int, screen_h: int) -> tuple[int, int]:
    """Keep the overlay fully on screen (e.g. after a monitor change)."""
    return (max(0, min(x, max(0, screen_w - w))),
            max(0, min(y, max(0, screen_h - h))))


def options_from_settings(settings) -> dict:
    return {key: getattr(settings, attr) for key, attr in OPTION_ATTRS.items()}


def apply_option(settings, key: str, value) -> None:
    """Change one overlay option on a Settings object (validated). Raises ValueError if invalid."""
    if key not in OPTION_ATTRS:
        raise ValueError(f"unknown option {key!r}")
    if key == "theme":
        if value not in THEMES:
            raise ValueError(f"unknown theme {value!r}")
    elif key in ("opacity", "scale"):
        value = float(value)
    else:
        value = bool(value)
    setattr(settings, OPTION_ATTRS[key], value)
    settings.validate()


def snapshot(counter, status: str = STATUS_MANUAL) -> dict:
    """Everything the overlay draws, taken from a ChestCounter."""
    return {
        "match": counter.match_count,
        "session": counter.session_count,
        "timer": format_timer(counter.match_elapsed()),
        "status": status,
    }
