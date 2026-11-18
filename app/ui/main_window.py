"""Main window: sidebar (Dashboard / Live Tracker / Settings) + pages. Dark, purple/blue cards."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QButtonGroup, QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QStackedWidget, QVBoxLayout, QWidget)

from app import APP_NAME, __version__
from app.ui.page_dashboard import DashboardPage
from app.ui.page_live import LivePage
from app.ui.page_settings import SettingsPage
from app.ui.theme import stylesheet


class MainWindow(QMainWindow):
    quit_requested = Signal()

    def __init__(self, controller):
        super().__init__()
        self.ctl = controller
        self.setWindowTitle(f"Fortnite Live Chest Tracker  v{__version__}")
        self.resize(1000, 680)
        self.setMinimumSize(820, 560)
        self.setStyleSheet(stylesheet(controller.settings.overlay_theme))

        root = QWidget()
        row = QHBoxLayout(root)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        side = QWidget()
        side.setObjectName("sidebar")
        side.setFixedWidth(200)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(12, 18, 12, 12)
        title = QLabel("CHEST TRACKER")
        title.setObjectName("appTitle")
        sl.addWidget(title)
        ver = QLabel(f"v{__version__}")
        ver.setObjectName("muted")
        sl.addWidget(ver)
        sl.addSpacing(14)

        self.stack = QStackedWidget()
        self.dashboard = DashboardPage(controller)
        self.live = LivePage(controller)
        self.settings_page = SettingsPage(controller)
        group = QButtonGroup(self)
        group.setExclusive(True)
        for i, (name, page) in enumerate((("Dashboard", self.dashboard),
                                          ("Live Tracker", self.live),
                                          ("Settings", self.settings_page))):
            self.stack.addWidget(page)
            btn = QPushButton(name)
            btn.setObjectName("nav")
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            btn.clicked.connect(lambda _=False, idx=i: self.show_page(idx))
            group.addButton(btn)
            sl.addWidget(btn)
        sl.addStretch(1)
        self.btn_stream = QPushButton()
        self.btn_stream.setMinimumHeight(40)
        self.btn_stream.clicked.connect(
            lambda: controller.set_overlay_visible(not controller.overlay_visible))
        sl.addWidget(self.btn_stream)
        self.refresh_stream_button()
        sl.addSpacing(8)
        note = QLabel("Closing this window\nquits the tracker.")
        note.setObjectName("hint")
        sl.addWidget(note)

        row.addWidget(side)
        row.addWidget(self.stack, 1)
        self.setCentralWidget(root)
        controller.subscribe(self.on_change)

    def refresh_stream_button(self) -> None:
        on = self.ctl.overlay_visible
        self.btn_stream.setText("Stop stream" if on else "Start stream")
        self.btn_stream.setObjectName("danger" if on else "primary")
        self.btn_stream.style().unpolish(self.btn_stream)     # re-apply the style sheet for the new id
        self.btn_stream.style().polish(self.btn_stream)

    def show_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        # Hidden pages skip the 1-second updates, so bring the page you just opened up to date.
        if index == 0:
            self.dashboard.on_change("match")       # cards + history table
        elif index == 1:
            self.live.refresh(rebuild_events=True)

    def on_change(self, kind: str) -> None:
        if kind == "stream":
            self.refresh_stream_button()
            return
        if kind == "settings":
            self.setStyleSheet(stylesheet(self.ctl.settings.overlay_theme))
            self.settings_page.load(self.ctl.settings)
        # Only refresh what you can see (the 1-second tick would otherwise rebuild hidden pages).
        current = self.stack.currentWidget()
        if current is self.dashboard or kind in ("match", "reset"):
            self.dashboard.on_change(kind)
        if current is self.live or kind in ("count", "match", "reset", "settings"):
            self.live.on_change(kind)

    def closeEvent(self, event) -> None:
        self.quit_requested.emit()
        event.accept()
