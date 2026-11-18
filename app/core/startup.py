"""Start-with-Windows (per-user Run registry key). No admin rights needed.

The registry is injected so the logic is unit-tested without Windows. On other systems
set_enabled() reports an error instead of crashing.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from app import APP_NAME

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


class WinRegistry:
    """HKEY_CURRENT_USER\\...\\Run value named after the app."""

    def __init__(self):
        import winreg
        self._w = winreg

    def get(self) -> str | None:
        try:
            with self._w.OpenKey(self._w.HKEY_CURRENT_USER, RUN_KEY) as k:
                return self._w.QueryValueEx(k, APP_NAME)[0]
        except FileNotFoundError:
            return None

    def set(self, command: str) -> None:
        with self._w.CreateKey(self._w.HKEY_CURRENT_USER, RUN_KEY) as k:
            self._w.SetValueEx(k, APP_NAME, 0, self._w.REG_SZ, command)

    def delete(self) -> None:
        try:
            with self._w.OpenKey(self._w.HKEY_CURRENT_USER, RUN_KEY, 0, self._w.KEY_SET_VALUE) as k:
                self._w.DeleteValue(k, APP_NAME)
        except FileNotFoundError:
            pass


def default_registry():
    try:
        return WinRegistry()
    except ImportError:
        return None   # not Windows


def startup_command(main_py: str | Path | None = None, python_exe: str | None = None) -> str:
    """Command Windows runs at login: the overlay only (no big window), without a console."""
    exe = Path(python_exe or sys.executable)
    pyw = exe.with_name("pythonw.exe")
    if exe.name.lower() == "python.exe" and pyw.exists():
        exe = pyw
    main = Path(main_py) if main_py else Path(__file__).resolve().parents[2] / "main.py"
    return f'"{exe}" "{main}" --overlay'


def is_enabled(registry="auto") -> bool:
    reg = default_registry() if registry == "auto" else registry
    if reg is None:
        return False
    try:
        return bool(reg.get())
    except OSError:
        return False


def set_enabled(enabled: bool, registry="auto", command: str | None = None) -> str | None:
    """Turn start-with-Windows on/off. Returns an error message, or None on success."""
    reg = default_registry() if registry == "auto" else registry
    if reg is None:
        return "Start with Windows is only available on Windows."
    try:
        if enabled:
            reg.set(command or startup_command())
        else:
            reg.delete()
    except OSError as e:
        return f"Could not change the Windows startup entry: {e}"
    return None
