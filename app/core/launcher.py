"""Logic behind the double-click start file (FortniteChestTracker.pyw). Testable without Windows.

Replaces run.bat: installs missing packages on first start, opens the app with no console
window, and shows errors in a message box instead of a black window that vanishes.
"""
from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys
import traceback
from pathlib import Path

from app import APP_NAME

# import name -> pip package name
REQUIRED = {"PySide6": "PySide6", "mss": "mss", "cv2": "opencv-python-headless",
            "numpy": "numpy", "keyboard": "keyboard"}


def missing_modules(find=importlib.util.find_spec) -> list[str]:
    return [m for m in REQUIRED if find(m) is None]


def console_python(python_exe: str | None = None) -> str:
    """pip needs python.exe; double-clicking a .pyw runs pythonw.exe."""
    exe = Path(python_exe or sys.executable)
    if exe.name.lower() == "pythonw.exe" and exe.with_name("python.exe").exists():
        return str(exe.with_name("python.exe"))
    return str(exe)


def install_requirements(requirements: Path, python_exe: str | None = None, run=subprocess.run) -> str | None:
    """pip install -r requirements.txt with no window. Returns an error message, or None on success."""
    cmd = [console_python(python_exe), "-m", "pip", "install", "-r", str(requirements)]
    try:
        r = run(cmd, capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except OSError as e:
        return f"Could not start pip: {e}"
    if r.returncode != 0:
        tail = (r.stderr or r.stdout or "").strip().splitlines()[-5:]
        return "Installing the required packages failed:\n" + "\n".join(tail)
    return None


def show_message(text: str, error: bool = False) -> None:
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, text, APP_NAME, 0x10 if error else 0x40)
    except Exception:   # not Windows / no GUI: fall back to the console
        print(f"{APP_NAME}: {text}")


def launch(argv: list[str], find=importlib.util.find_spec, installer=install_requirements,
           notify=show_message, entry=None) -> int:
    """Install what is missing, then run main.py. No arguments = open the main window (--app)."""
    root = Path(__file__).resolve().parents[2]
    missing = missing_modules(find)
    if missing:
        notify("First start: installing the packages the tracker needs (" + ", ".join(missing) + ").\n"
               "This can take a minute or two. Click OK and wait - the app opens by itself when it is done.")
        err = installer(root / "requirements.txt")
        importlib.invalidate_caches()
        if err is None and missing_modules(find):
            err = "Some packages are still missing after the install: " + ", ".join(missing_modules(find))
        if err:
            notify(err + "\n\nCheck your internet connection, then try again.", error=True)
            return 1
    if entry is None:
        from main import main as entry
    sys.argv = ["main.py", *(argv or ["--app"])]
    try:
        return entry()
    except Exception:
        notify("The tracker crashed:\n\n" + "\n".join(traceback.format_exc().strip().splitlines()[-6:]), error=True)
        return 1
