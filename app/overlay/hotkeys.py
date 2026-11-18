"""Global hotkeys (uses the `keyboard` package). Emits a Qt signal per action.

The hotkey callbacks run on the keyboard library's own thread, so they only emit a signal;
all real work happens on the Qt main thread.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class HotkeyManager(QObject):
    triggered = Signal(str)   # action name, e.g. "add_chest"

    def __init__(self):
        super().__init__()
        self.active: list[str] = []
        self.problems: list[str] = []
        self._keyboard = None

    def start(self, bindings: dict[str, str], problems: list[str]) -> bool:
        self.problems = list(problems)
        try:
            import keyboard
        except ImportError:
            self.problems.append("the 'keyboard' package is missing (python -m pip install -r requirements.txt)")
            return False
        self._keyboard = keyboard
        for action, hotkey in bindings.items():
            try:
                keyboard.add_hotkey(hotkey, lambda a=action: self.triggered.emit(a))
                self.active.append(action)
            except Exception as e:  # invalid key name etc.
                self.problems.append(f"{action} ({hotkey!r}): {e}")
        return bool(self.active)

    def has(self, action: str) -> bool:
        return action in self.active

    def stop(self) -> None:
        if self._keyboard is not None:
            try:
                self._keyboard.unhook_all_hotkeys()
            except Exception:
                pass
