"""A small bar chart: chests per match. Drawn with QPainter (no extra dependency)."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QWidget

from app.overlay.model import THEMES
from app.ui.dashboard_model import bar_fractions

MUTED = QColor(160, 160, 190)


class BarChart(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(150)
        self.values: list[int] = []
        self.theme = "violet"

    def set_data(self, values: list[int], theme: str) -> None:
        self.values, self.theme = list(values), theme
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        p.setFont(QFont("Segoe UI", 9))
        if not self.values:
            p.setPen(MUTED)
            p.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, "Finished matches will show up here.")
            p.end()
            return
        a1 = QColor(*THEMES.get(self.theme, THEMES["violet"])[0])
        a2 = QColor(*THEMES.get(self.theme, THEMES["violet"])[1])
        top_pad, bottom_pad = 18, 6
        plot_h = h - top_pad - bottom_pad
        n = len(self.values)
        slot = w / n
        bar_w = max(4.0, slot * 0.62)
        show_labels = bar_w >= 16
        p.setPen(QPen(MUTED, 1))
        p.drawLine(0, int(h - bottom_pad), w, int(h - bottom_pad))
        for i, frac in enumerate(bar_fractions(self.values)):
            bh = max(2.0, frac * plot_h) if self.values[i] > 0 else 0.0
            x = i * slot + (slot - bar_w) / 2
            y = h - bottom_pad - bh
            grad = QLinearGradient(0, y, 0, y + max(bh, 1))
            grad.setColorAt(0, a1)
            grad.setColorAt(1, a2)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(grad)
            p.drawRoundedRect(QRectF(x, y, bar_w, bh), 3, 3)
            if show_labels:
                p.setPen(MUTED)
                p.drawText(QRectF(x - 6, y - 16, bar_w + 12, 14), Qt.AlignmentFlag.AlignCenter, str(self.values[i]))
        p.end()
