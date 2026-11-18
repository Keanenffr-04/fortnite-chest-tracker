"""Wires settings + controller + hotkeys + overlay (+ main window) together.

  python main.py --overlay   overlay only (also what "start with Windows" runs)
  python main.py --app       main window + overlay (default for run.bat)

All state lives in TrackerController; this file only connects it to Qt and the hotkeys.
"""
from __future__ import annotations

import sys

from app.config.settings import Settings, app_data_dir
from app.core.controller import TrackerController
from app.core.sound import SoundPlayer
from app.database.db import Database
from app.overlay.hotkey_map import build_bindings
from app.overlay.model import clamp_position, options_from_settings, scaled_size, snapshot


def run_overlay(with_window: bool = False) -> int:
    try:
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication
        from app.overlay.hotkeys import HotkeyManager
        from app.overlay.window import OverlayWindow
        if with_window:
            from app.ui.main_window import MainWindow
    except ImportError:
        print("PySide6 is missing. Run: python -m pip install -r requirements.txt")
        return 1

    settings = Settings.load()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")          # consistent look so the dark style sheet applies everywhere
    db = Database(app_data_dir() / "chests.db")
    sound = SoundPlayer(app_data_dir() / "sounds", settings.sound_enabled, settings.sound_volume)
    # With the main window the overlay stays hidden until you press Start stream.
    ctl = TrackerController(settings, db, sound, overlay_visible=not with_window)

    win = OverlayWindow(options_from_settings(settings))
    screen = app.primaryScreen().availableGeometry()

    def place():
        footer = settings.overlay_show_session or settings.overlay_show_timer
        w, h = scaled_size(settings.overlay_scale, footer)
        x, y = clamp_position(settings.overlay_x, settings.overlay_y, w, h, screen.width(), screen.height())
        win.move(x, y)

    def refresh():
        win.set_snapshot(snapshot(ctl.counter, ctl.status))

    # ---- hotkeys ----
    hk = HotkeyManager()
    state = {"can_unhide": False, "can_unlock": False, "bindings": None}

    def start_hotkeys(reload: bool):
        bindings, problems = build_bindings(settings)
        if reload and bindings == state["bindings"]:
            return                      # no hotkey changed: leave the registered ones alone
        state["bindings"] = dict(bindings)
        (hk.reload if reload else hk.start)(bindings, problems)
        for line in hk.problems:
            print(f"Hotkey problem: {line}")
        state["can_unhide"] = hk.has("toggle_overlay")
        state["can_unlock"] = hk.has("toggle_click_through")
        # Never let the user get stuck: hide / lock are only offered when something can undo them.
        # With the main window open, the window itself can always undo them.
        win.hotkeys_active = with_window or (state["can_unhide"] and state["can_unlock"])
        if hk.active:
            print("Hotkeys active: " + ", ".join(f"{a}={bindings[a]}" for a in hk.active))

    actions = {
        "toggle_overlay": lambda: ctl.set_overlay_visible(not win.isVisible()),
        "add_chest": ctl.add,
        "remove_chest": ctl.remove,
        "toggle_click_through": lambda: ctl.set_click_through(not win.locked),
        "quit": app.quit,
    }
    hk.triggered.connect(lambda name: actions[name]())
    start_hotkeys(reload=False)
    app.aboutToQuit.connect(hk.stop)

    # ---- keep the overlay in step with settings ----
    def sync_overlay():
        win.apply_options(options_from_settings(settings))
        place()
        undoable = with_window or state["can_unhide"]
        want_visible = ctl.overlay_visible or not undoable    # never leave it hidden for good
        if win.isVisible() != want_visible:
            win.setVisible(want_visible)
        want_lock = settings.overlay_click_through and (with_window or state["can_unlock"])
        if win.locked != want_lock:
            win.set_click_through(want_lock)

    def on_change(kind: str):
        if kind == "settings":
            start_hotkeys(reload=True)
            sync_overlay()
        elif kind == "stream":
            sync_overlay()
        refresh()

    ctl.subscribe(on_change)
    sync_overlay()
    refresh()

    # ---- overlay -> controller ----
    win.hide_requested.connect(lambda: ctl.set_overlay_visible(False))
    win.click_through_requested.connect(lambda: ctl.set_click_through(not win.locked))
    win.chest_added.connect(ctl.add)
    win.chest_removed.connect(ctl.remove)
    win.new_match_requested.connect(ctl.new_match)
    win.option_changed.connect(ctl.set_option)
    win.quit_requested.connect(app.quit)
    win.moved.connect(ctl.set_overlay_position)
    app.aboutToQuit.connect(ctl.finish)

    tick = QTimer()
    tick.timeout.connect(ctl.tick)
    tick.start(1000)

    main = None
    if with_window:
        main = MainWindow(ctl)
        main.quit_requested.connect(app.quit)
        main.show()
    return app.exec()


def run_app() -> int:
    return run_overlay(with_window=True)
