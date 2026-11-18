"""Live Tracker page: big counter, status, manual correction, recent events."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget

from app.overlay.model import format_timer
from app.ui.dashboard_model import recent_event_lines


class LivePage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.setObjectName("page")
        self.ctl = controller
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(12)

        title = QLabel("Live Tracker")
        title.setObjectName("pageTitle")
        lay.addWidget(title)

        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(18, 14, 18, 14)
        cl.setSpacing(4)
        top = QHBoxLayout()
        self.status = QLabel("")
        self.status.setObjectName("status")
        self.timer = QLabel("00:00")
        self.timer.setObjectName("muted")
        top.addWidget(self.status)
        top.addStretch(1)
        top.addWidget(self.timer)
        cl.addLayout(top)
        cap = QLabel("CHESTS OPENED THIS MATCH")
        cap.setObjectName("muted")
        cap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(cap)
        self.big = QLabel("0")
        self.big.setObjectName("bigCount")
        self.big.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self.big)
        self.session = QLabel("")
        self.session.setObjectName("muted")
        self.session.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self.session)
        lay.addWidget(card)

        row = QHBoxLayout()
        self.btn_add = QPushButton("+1 Chest")
        self.btn_add.setObjectName("primary")
        self.btn_remove = QPushButton("-1 Chest")
        self.btn_new = QPushButton("New match")
        self.btn_add.setToolTip("Count a chest (same as your add-chest hotkey).")
        self.btn_remove.setToolTip("Undo a miscount (same as your remove-chest hotkey).")
        self.btn_new.setToolTip("Save this match to History and start a fresh one.")
        for b in (self.btn_add, self.btn_remove, self.btn_new):
            b.setMinimumHeight(44)
            row.addWidget(b)
        lay.addLayout(row)

        sub = QLabel("What happened this match (newest first)")
        sub.setObjectName("sectionTitle")
        lay.addWidget(sub)
        self.events = QListWidget()
        lay.addWidget(self.events, 1)

        self.btn_add.clicked.connect(self.ctl.add)
        self.btn_remove.clicked.connect(self.ctl.remove)
        self.btn_new.clicked.connect(self.ctl.new_match)
        self.refresh(rebuild_events=True)

    def refresh(self, rebuild_events: bool = False) -> None:
        c = self.ctl.counter
        self.big.setText(str(c.match_count))
        self.session.setText(f"Session total: {c.session_count}")
        self.timer.setText(f"Match time  {format_timer(c.match_elapsed())}")
        self.status.setText(self.ctl.status)
        if rebuild_events:
            self.events.clear()
            lines = recent_event_lines(self.ctl.recent_events())
            self.events.addItems(lines or ["Nothing yet. Press +1 Chest when you open one."])

    def on_change(self, kind: str) -> None:
        self.refresh(rebuild_events=kind in ("count", "match", "reset"))
