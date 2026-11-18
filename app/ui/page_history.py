"""History page: every finished match + an Export CSV button."""
from __future__ import annotations

import time
from datetime import date, timedelta
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (QAbstractItemView, QFileDialog, QFrame, QHBoxLayout, QHeaderView, QLabel,
                               QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from app.ui.dashboard_model import (best_flags, chests_label, day_summary, day_title, day_totals,
                                    export_filename, format_match_row, history_summary)


class HistoryPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.setObjectName("page")
        self.ctl = controller
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(12)

        top = QHBoxLayout()
        title = QLabel("History")
        title.setObjectName("pageTitle")
        top.addWidget(title)
        top.addStretch(1)
        self.btn_export = QPushButton("Export CSV")
        self.btn_export.setObjectName("primary")
        self.btn_export.setMinimumHeight(38)
        self.btn_export.clicked.connect(self.export)
        top.addWidget(self.btn_export)
        lay.addLayout(top)

        lay.addWidget(self._build_day_card())

        self.summary = QLabel("")
        self.summary.setObjectName("muted")
        lay.addWidget(self.summary)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["#", "Started", "Duration", "Chests"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(30)
        lay.addWidget(self.table, 1)

        self.empty = QLabel("No finished matches yet. Press \"New match\" on the Live Tracker to save the current one.")
        self.empty.setObjectName("muted")
        self.empty.setWordWrap(True)
        lay.addWidget(self.empty)

        hint = QLabel("\u2605 = your personal best. The match in progress is counted in the chests-opened card for today, but is not listed or exported until you press New match.")
        hint.setObjectName("hint")
        lay.addWidget(hint)
        self.refresh()

    # ---- chests on one day -------------------------------------------------
    def _build_day_card(self) -> QFrame:
        """A card to pick a day (arrows / Today) and see how many chests you opened on it."""
        self.days_back = 0                                    # 0 = today; follows midnight automatically
        card = QFrame()
        card.setObjectName("card")
        row = QHBoxLayout(card)
        row.setContentsMargins(18, 12, 18, 12)
        row.setSpacing(10)
        self.btn_prev = QPushButton("\u25C0")
        self.btn_next = QPushButton("\u25B6")
        self.btn_today = QPushButton("Today")
        for b in (self.btn_prev, self.btn_next):
            b.setObjectName("step")
            b.setFixedSize(36, 36)
        self.btn_prev.setToolTip("Previous day")
        self.btn_next.setToolTip("Next day")
        self.btn_prev.clicked.connect(lambda: self.move_day(1))
        self.btn_next.clicked.connect(lambda: self.move_day(-1))
        self.btn_today.clicked.connect(lambda: self.move_day(-self.days_back))
        row.addWidget(self.btn_prev)
        row.addWidget(self.btn_next)
        names = QVBoxLayout()
        names.setSpacing(0)
        self.day_name = QLabel("")
        self.day_name.setObjectName("sectionTitle")
        self.day_name.setStyleSheet("margin-top: 0px;")
        self.day_date = QLabel("")
        self.day_date.setObjectName("muted")
        names.addWidget(self.day_name)
        names.addWidget(self.day_date)
        row.addLayout(names)
        row.addWidget(self.btn_today)
        row.addStretch(1)
        self.day_matches = QLabel("")
        self.day_matches.setObjectName("muted")
        row.addWidget(self.day_matches)
        self.day_chests = QLabel("0")
        self.day_chests.setObjectName("cardValue")
        row.addWidget(self.day_chests)
        unit = QLabel("chests\nopened")
        unit.setObjectName("muted")
        row.addWidget(unit)
        self.refresh_day()
        return card

    def move_day(self, delta: int) -> None:
        self.days_back = max(0, self.days_back + delta)
        self.refresh_day()

    def refresh_day(self) -> None:
        today = date.today()
        d = today - timedelta(days=self.days_back)
        chests, matches = day_totals(self.ctl.db, self.ctl.counter, d)
        self.day_name.setText(day_title(d, today))
        self.day_date.setText(d.strftime("%A %d %B %Y"))
        self.day_chests.setText(str(chests))
        self.day_matches.setText(day_summary(chests, matches))
        self.btn_next.setEnabled(self.days_back > 0)
        self.btn_today.setEnabled(self.days_back > 0)

    def refresh(self) -> None:
        self.refresh_day()
        rows = self.ctl.db.all_matches()
        self.summary.setText(history_summary(rows))
        self.table.setRowCount(len(rows))
        flags = best_flags(rows)
        for r, row in enumerate(rows):
            cells = (str(len(rows) - r),) + format_match_row(row)    # oldest match = #1
            cells = cells[:3] + (chests_label(cells[3], flags[r]),)
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if c in (0, 3):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if flags[r]:                              # personal best: gold + bold
                    item.setForeground(QColor("#f5c542"))
                    f = QFont(item.font()); f.setBold(True); item.setFont(f)
                self.table.setItem(r, c, item)
        self.empty.setVisible(not rows)
        self.table.setVisible(bool(rows))
        self.btn_export.setEnabled(bool(rows))

    def export(self) -> None:
        start = str(Path(self.ctl.settings.data_dir) / export_filename(time.time()))
        path, _ = QFileDialog.getSaveFileName(self, "Export matches", start, "CSV files (*.csv)")
        if not path:
            return                                   # cancelled
        count, error = self.ctl.export_matches(path)
        if error:
            QMessageBox.warning(self, "Export failed", error)
        else:
            QMessageBox.information(self, "Export done", f"Saved {count} match{'es' if count != 1 else ''} to:\n{path}")

    def on_change(self, kind: str) -> None:
        if kind in ("match", "reset"):
            self.refresh()
        elif kind in ("count", "tick"):
            self.refresh_day()                       # the match in progress counts as today
