"""What the Settings page shows and how changes are validated. No Qt, so it is unit-tested.

The page builds its widgets from SECTIONS, so adding a setting later = adding one Field here.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from app.config.settings import THEME_NAMES, Settings
from app.overlay.hotkey_map import build_bindings


@dataclass(frozen=True)
class Field:
    key: str                  # attribute name on Settings
    label: str
    kind: str                 # bool | percent | float | int | choice | hotkey
    minimum: float = 0.0
    maximum: float = 1.0
    step: float = 0.1
    choices: tuple = ()       # ((value, label), ...) for kind == "choice"
    hint: str = ""


_THEMES = tuple((n, n.capitalize()) for n in THEME_NAMES)
_HK = "Empty = disabled. Needs ctrl/alt/shift, e.g. ctrl+shift+o"

SECTIONS: tuple[tuple[str, tuple[Field, ...]], ...] = (
    ("Overlay", (
        Field("overlay_visible", "Show overlay", "bool"),
        Field("overlay_click_through", "Click-through (LOCKED)", "bool",
              hint="Mouse clicks pass through to the game. Undo with its hotkey or here."),
        Field("overlay_opacity", "Opacity", "percent", 0.1, 1.0),
        Field("overlay_scale", "Size", "float", 0.5, 3.0, 0.1, hint="1.0 = normal"),
        Field("overlay_theme", "Theme", "choice", choices=_THEMES),
        Field("overlay_show_status", "Show status", "bool"),
        Field("overlay_show_session", "Show session count", "bool"),
        Field("overlay_show_timer", "Show match timer", "bool"),
    )),
    ("Hotkeys", (
        Field("hotkey_toggle_overlay", "Hide / show overlay", "hotkey", hint=_HK),
        Field("hotkey_add_chest", "Add a chest", "hotkey", hint=_HK),
        Field("hotkey_remove_chest", "Remove a chest", "hotkey", hint=_HK),
        Field("hotkey_toggle_click_through", "Click-through on/off", "hotkey", hint=_HK),
        Field("hotkey_quit", "Quit", "hotkey", hint=_HK),
    )),
    ("Detection", (
        Field("detection_sensitivity", "Sensitivity", "percent", 0.0, 1.0,
              hint="Minimum confidence to count. Detection itself arrives in v1.1.8."),
        Field("detection_cooldown_s", "Cooldown (seconds)", "float", 0.0, 10.0, 0.1,
              hint="Ignore repeat detections inside this window."),
        Field("detection_interval_ms", "Scan interval (ms)", "int", 20, 1000, 10),
    )),
    ("Sound", (
        Field("sound_enabled", "Play sounds", "bool"),
        Field("sound_volume", "Volume", "percent", 0.0, 1.0),
    )),
    ("Startup", (
        Field("start_with_windows", "Start with Windows", "bool",
              hint="Starts the overlay at login (no big window)."),
    )),
)

FIELDS: dict[str, Field] = {f.key: f for _, fields_ in SECTIONS for f in fields_}


def coerce(field: Field, value):
    """Convert a widget value to the right type. Raises ValueError/TypeError if unusable."""
    k = field.kind
    if k == "bool":
        return bool(value)
    if k in ("percent", "float"):
        return float(value)
    if k == "int":
        return int(value)
    if k == "choice":
        if value not in [v for v, _ in field.choices]:
            raise ValueError(f"{value!r} is not an allowed choice")
        return value
    if k == "hotkey":
        return str(value).strip()
    raise ValueError(f"unknown field kind {k!r}")


def current_values(settings: Settings) -> dict:
    return {key: getattr(settings, key) for key in FIELDS}


def apply_changes(current: Settings, changes: dict) -> tuple[Settings | None, list[str]]:
    """Validate `changes` on a COPY of `current`. All-or-nothing:
    returns (new_settings, []) or (None, [problems]) and never half-applies."""
    new = replace(current)
    problems: list[str] = []
    for key, value in changes.items():
        f = FIELDS.get(key)
        if f is None:
            problems.append(f"Unknown setting {key!r}")
            continue
        try:
            setattr(new, key, coerce(f, value))
        except (TypeError, ValueError):
            problems.append(f"{f.label}: {value!r} is not valid")
    if problems:
        return None, problems
    new.validate()
    _, hotkey_problems = build_bindings(new)
    if hotkey_problems:
        return None, hotkey_problems
    return new, []


def defaults_keeping(current: Settings) -> Settings:
    """Factory defaults, but keep where the data lives and where the overlay sits."""
    fresh = Settings()
    fresh.data_dir = current.data_dir
    fresh.overlay_x, fresh.overlay_y = current.overlay_x, current.overlay_y
    return fresh
