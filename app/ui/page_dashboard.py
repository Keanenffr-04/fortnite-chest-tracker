"""Dashboard page: stat cards + recent matches. (Charts and full history come in v1.1.7.)"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QAbstractItemView, QGridLayout, QHeaderView, QLabel, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from app.ui.dashboard_model import DETECTION_BANNER, format_match_row, stat_cards
from app.ui.widgets import Card

HISTORY_ROWS = 10


class DashboardPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.setObjectName("page")
        self.ctl = controller
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(14)

        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")
        lay.addWidget(title)

        self.banner = QLabel(DETECTION_BANNER)
        self.banner.setObjectName("banner")
        self.banner.setWordWrap(True)
        lay.addWidget(self.banner)

        grid = QGridLayout()
        grid.setSpacing(12)
        self.cards: list[Card] = []
        for i, (label, value) in enumerate(stat_cards(self.ctl.stats())):
            card = Card(label, value)
            self.cards.append(card)
            grid.addWidget(card, i // 3, i % 3)
        lay.addLayout(grid)

        sub = QLabel(f"Recent matches (last {HISTORY_ROWS})")
        sub.setObjectName("sectionTitle")
        lay.addWidget(sub)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Started", "Duration", "Chests"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        lay.addWidget(self.table, 1)

        self.empty = QLabel("No finished matches yet. Press \"New match\" on the Live Tracker "
                            "to save the current one.")
        self.empty.setObjectName("muted")
        self.empty.setWordWrap(True)
        lay.addWidget(self.empty)
        self.refresh_table()

    def refresh_cards(self) -> None:
        for card, (_, value) in zip(self.cards, stat_cards(self.ctl.stats())):
            card.set_value(value)

    def refresh_table(self) -> None:
        rows = self.ctl.db.recent_matches(HISTORY_ROWS)
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, text in enumerate(format_match_row(row)):
                item = QTableWidgetItem(text)
                if c == 2:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(r, c, item)
        self.empty.setVisible(not rows)
        self.table.setVisible(bool(rows))

    def on_change(self, kind: str) -> None:
        self.refresh_cards()
        if kind in ("match", "reset"):
            self.refresh_table()
