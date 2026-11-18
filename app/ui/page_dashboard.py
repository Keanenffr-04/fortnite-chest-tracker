"""Dashboard page: stat cards + recent matches. Chart of chests per match; Today / Last 7 days cards. Full history + CSV export: History page."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QAbstractItemView, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QPushButton, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from app.ui.chart import BarChart
from app.ui.dashboard_model import (DETECTION_BANNER, chart_values, daily_values, format_match_row,
                                    stat_cards)
from app.ui.widgets import Card

HISTORY_ROWS = 5


class DashboardPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.setObjectName("page")
        self.ctl = controller
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(10)

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
            grid.addWidget(card, i // 4, i % 4)
        lay.addLayout(grid)

        self.per_day = False
        cap_row = QHBoxLayout()
        self.cap = QLabel("")
        self.cap.setObjectName("sectionTitle")
        cap_row.addWidget(self.cap)
        cap_row.addStretch(1)
        self.btn_mode = QPushButton("Show per day")
        self.btn_mode.clicked.connect(self.toggle_chart)
        cap_row.addWidget(self.btn_mode)
        lay.addLayout(cap_row)
        self.chart = BarChart()
        lay.addWidget(self.chart)

        sub = QLabel(f"Recent matches (last {HISTORY_ROWS}, see History for all)")
        sub.setObjectName("sectionTitle")
        lay.addWidget(sub)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Started", "Duration", "Chests"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(30)
        lay.addWidget(self.table, 1)

        self.empty = QLabel("No finished matches yet. Press \"New match\" on the Live Tracker "
                            "to save the current one.")
        self.empty.setObjectName("muted")
        self.empty.setWordWrap(True)
        lay.addWidget(self.empty)
        self.refresh_table()
        self.refresh_chart()

    def toggle_chart(self) -> None:
        self.per_day = not self.per_day
        self.refresh_chart()

    def refresh_chart(self) -> None:
        if self.per_day:
            vals = daily_values(self.ctl.db, self.ctl.counter)
            self.cap.setText("Chests per day (last 14 days, today on the right)")
            self.btn_mode.setText("Show per match")
        else:
            vals = chart_values(self.ctl.db, self.ctl.counter)
            self.cap.setText("Chests per match (last 20, newest on the right)")
            self.btn_mode.setText("Show per day")
        self.chart.set_data(vals, self.ctl.settings.overlay_theme)

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
        if kind in ("count", "match", "reset", "settings"):
            self.refresh_chart()
        if kind in ("match", "reset"):
            self.refresh_table()
