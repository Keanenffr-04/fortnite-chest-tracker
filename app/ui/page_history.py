"""History page: every finished match + an Export CSV button."""
from __future__ import annotations

import time
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (QAbstractItemView, QFileDialog, QHBoxLayout, QHeaderView, QLabel,
                               QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from app.ui.dashboard_model import (best_flags, chests_label, export_filename, format_match_row,
                                    history_summary)


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

        self.summary = QLabel("")
        self.summary.setObjectName("muted")
        lay.addWidget(self.summary)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["#", "Started", "Duration", "Chests"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        lay.addWidget(self.table, 1)

        self.empty = QLabel("No finished matches yet. Press \"New match\" on the Live Tracker to save the current one.")
        self.empty.setObjectName("muted")
        self.empty.setWordWrap(True)
        lay.addWidget(self.empty)

        hint = QLabel("\u2605 = your personal best. The match in progress is not listed or exported until you press New match.")
        hint.setObjectName("hint")
        lay.addWidget(hint)
        self.refresh()

    def refresh(self) -> None:
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
