"""Wires settings + counter + database + overlay window together (`python main.py --overlay`)."""
from __future__ import annotations

import sys
import time

from app.config.settings import Settings, app_data_dir
from app.core.counter import ChestCounter
from app.database.db import Database
from app.overlay.model import STATUS_MANUAL, clamp_position, scaled_size, snapshot


def run_overlay() -> int:
    try:
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication
        from app.overlay.window import OverlayWindow
    except ImportError:
        print("PySide6 is missing. Run: python -m pip install -r requirements.txt")
        return 1

    settings = Settings.load()
    app = QApplication(sys.argv)
    db = Database(app_data_dir() / "chests.db")
    session_id = db.start_session(time.time())
    counter = ChestCounter(settings.detection_sensitivity, settings.detection_cooldown_s)

    win = OverlayWindow(settings.overlay_scale, settings.overlay_opacity)
    screen = app.primaryScreen().availableGeometry()
    w, h = scaled_size(settings.overlay_scale)
    x, y = clamp_position(settings.overlay_x, settings.overlay_y, w, h, screen.width(), screen.height())
    win.move(x, y)

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
        refresh()

    def remove():
        counter.manual_adjust(-1)
        refresh()

    win.chest_added.connect(add)
    win.chest_removed.connect(remove)
    win.new_match_requested.connect(new_match)
    win.quit_requested.connect(app.quit)
    win.moved.connect(save_position)
    app.aboutToQuit.connect(finish)

    tick = QTimer()
    tick.timeout.connect(refresh)
    tick.start(1000)

    refresh()
    win.show()
    return app.exec()
