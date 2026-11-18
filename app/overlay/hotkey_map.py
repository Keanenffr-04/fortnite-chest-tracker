"""Hotkey rules (no Qt, no keyboard library, so it is unit-tested).

Turns the hotkey strings in Settings into a validated action -> hotkey map.
A hotkey is rejected if it would fire during normal play/typing (single plain letter or
number with no modifier) or if two actions share the same combination.
Empty string = disabled.
"""
from __future__ import annotations

import re

ACTIONS = {
    "toggle_overlay": "hotkey_toggle_overlay",
    "add_chest": "hotkey_add_chest",
    "remove_chest": "hotkey_remove_chest",
    "toggle_click_through": "hotkey_toggle_click_through",
    "quit": "hotkey_quit",
}
MODIFIERS = {"ctrl", "alt", "shift", "windows"}
_ALIASES = {"control": "ctrl", "win": "windows", "cmd": "windows", "option": "alt"}


def normalise(hotkey: str) -> str:
    parts = [p.strip().lower() for p in (hotkey or "").split("+")]
    return "+".join(_ALIASES.get(p, p) for p in parts if p)


def check(hotkey: str) -> str | None:
    """Return a problem description, or None if the hotkey is acceptable."""
    hk = normalise(hotkey)
    if not hk:
        return None
    parts = hk.split("+")
    key = parts[-1]
    if key in MODIFIERS:
        return "needs a non-modifier key (e.g. ctrl+shift+o)"
    has_modifier = any(p in MODIFIERS for p in parts[:-1])
    if not has_modifier and not re.fullmatch(r"f([1-9]|1[0-9]|2[0-4])", key):
        return "needs ctrl/alt/shift (a bare key would trigger while you play)"
    return None


def build_bindings(settings) -> tuple[dict[str, str], list[str]]:
    """Return ({action: hotkey}, [problems]). Problem hotkeys are left out of the map."""
    bindings: dict[str, str] = {}
    problems: list[str] = []
    used: dict[str, str] = {}
    for action, attr in ACTIONS.items():
        raw = getattr(settings, attr, "")
        hk = normalise(raw)
        if not hk:
            continue
        issue = check(hk)
        if issue:
            problems.append(f"{action} ({raw!r}): {issue}")
            continue
        if hk in used:
            problems.append(f"{action} ({raw!r}): already used by {used[hk]}")
            continue
        used[hk] = action
        bindings[action] = hk
    return bindings, problems
