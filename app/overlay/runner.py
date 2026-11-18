"""Wires settings + counter + database + sound + hotkeys + overlay together (`python main.py --overlay`)."""
from __future__ import annotations

import sys
import time

from app.config.settings import Settings, app_data_dir
from app.core.counter import ChestCounter
from app.core.sound import SoundPlayer
from app.database.db import Database
from app.overlay.hotkey_map import build_bindings
from app.overlay.model import (STATUS_MANUAL, apply_option, clamp_position,
                               options_from_settings, scaled_size, snapshot)


def run_overlay() -> int:
    try:
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication
        from app.overlay.hotkeys import HotkeyManager
        from app.overlay.window import OverlayWindow
    except ImportError:
        print("PySide6 is missing. Run: python -m pip install -r requirements.txt")
        return 1

    settings = Settings.load()
    app = QApplication(sys.argv)
    db = Database(app_data_dir() / "chests.db")
    session_id = db.start_session(time.time())
    counter = ChestCounter(settings.detection_sensitivity, settings.detection_cooldown_s)
    sound = SoundPlayer(app_data_dir() / "sounds", settings.sound_enabled, settings.sound_volume)

    win = OverlayWindow(options_from_settings(settings))
    screen = app.primaryScreen().availableGeometry()

    def place():
        footer = settings.overlay_show_session or settings.overlay_show_timer
        w, h = scaled_size(settings.overlay_scale, footer)
        x, y = clamp_position(settings.overlay_x, settings.overlay_y, w, h, screen.width(), screen.height())
        win.move(x, y)

    place()

    def refresh():
        win.set_snapshot(snapshot(counter, STATUS_MANUAL))

    def save_position(px, py):
        settings.overlay_x, settings.overlay_y = px, py
        settings.save()

    def store_match():
        summary = counter.new_match()
        if summary["chests"] > 0:           # don't store empty matches
            db.save_match(summary, session_id)

    def new_match():
        store_match()
        refresh()

    def finish():
        store_match()
        db.end_session(session_id, time.time())
        db.close()

    def add():
        counter.manual_adjust(1)
        sound.play_up()
        refresh()

    def remove():
        had_chest = counter.match_count > 0
        counter.manual_adjust(-1)
        if had_chest:
            sound.play_down()
        refresh()

    def on_option(key, value):
        try:
            apply_option(settings, key, value)
        except ValueError as e:
            print(f"Ignored option change: {e}")
            return
        settings.save()
        win.apply_options(options_from_settings(settings))
        sound.update(settings.sound_enabled, settings.sound_volume)
        place()
        refresh()

    def toggle_visible():
        win.setVisible(not win.isVisible())
        settings.overlay_visible = win.isVisible()
        settings.save()

    def toggle_click_through():
        settings.overlay_click_through = not win.locked
        win.set_click_through(settings.overlay_click_through)
        settings.save()

    actions = {
        "toggle_overlay": toggle_visible,
        "add_chest": add,
        "remove_chest": remove,
        "toggle_click_through": toggle_click_through,
        "quit": app.quit,
    }

    # ---- hotkeys ----
    bindings, problems = build_bindings(settings)
    hk = HotkeyManager()
    hk.triggered.connect(lambda name: actions[name]())
    hk.start(bindings, problems)
    for line in hk.problems:
        print(f"Hotkey problem: {line}")
    # Never let the user get stuck: hide / lock are only offered when a hotkey can undo them.
    can_unhide = hk.has("toggle_overlay")
    can_unlock = hk.has("toggle_click_through")
    win.hotkeys_active = can_unhide and can_unlock
    if hk.active:
        print("Hotkeys active: " + ", ".join(f"{a}={bindings[a]}" for a in hk.active))
    app.aboutToQuit.connect(hk.stop)

    win.hide_requested.connect(toggle_visible)
    win.click_through_requested.connect(toggle_click_through)
    win.chest_added.connect(add)
    win.chest_removed.connect(remove)
    win.new_match_requested.connect(new_match)
    win.option_changed.connect(on_option)
    win.quit_requested.connect(app.quit)
    win.moved.connect(save_position)
    app.aboutToQuit.connect(finish)

    tick = QTimer()
    tick.timeout.connect(refresh)
    tick.start(1000)

    refresh()
    if settings.overlay_visible or not can_unhide:
        win.show()
    if settings.overlay_click_through and can_unlock:
        win.set_click_through(True)
    return app.exec()
