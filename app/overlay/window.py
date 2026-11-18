"""The floating overlay window (PySide6). Custom-painted: dark, rounded, purple/blue accents.

Right-click for: add / remove a chest, new match, quit.
Drag with the left mouse button to move it; the position is saved.
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QMenu, QWidget

from app.overlay.model import STATUS_ERROR, STATUS_MANUAL, STATUS_WATCHING, scaled_size

BG_TOP = QColor(24, 20, 44)
BG_BOTTOM = QColor(12, 12, 24)
PURPLE = QColor(168, 85, 247)
BLUE = QColor(59, 130, 246)
RED = QColor(239, 68, 68)
WHITE = QColor(245, 245, 255)
MUTED = QColor(160, 160, 190)


class OverlayWindow(QWidget):
    chest_added = Signal()
    chest_removed = Signal()
    new_match_requested = Signal()
    quit_requested = Signal()
    moved = Signal(int, int)
    hide_requested = Signal()
    click_through_requested = Signal()

    def __init__(self, scale: float = 1.0, opacity: float = 0.85):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._scale = scale
        self._data = {"match": 0, "session": 0, "timer": "00:00", "status": STATUS_MANUAL}
        self._drag_offset = None
        self.locked = False            # click-through on
        self.hotkeys_active = False    # menu items for hide/lock only appear if hotkeys can undo them
        self.apply_appearance(scale, opacity)

    def apply_appearance(self, scale: float, opacity: float) -> None:
        self._scale = scale
        w, h = scaled_size(scale)
        self.setFixedSize(w, h)
        self.setWindowOpacity(min(1.0, max(0.1, opacity)))
        self.update()

    def set_click_through(self, on: bool) -> None:
        """Mouse clicks pass through the overlay to the game. Changing the flag hides the window in Qt,
        so show it again if it was visible."""
        was_visible = self.isVisible()
        self.locked = on
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, on)
        if was_visible:
            self.show()
        self.update()

    def set_snapshot(self, data: dict) -> None:
        self._data = data
        self.update()

    # ---- painting -------------------------------------------------------
    def paintEvent(self, _event) -> None:
        k = self._scale
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        rect = QRectF(2, 2, w - 4, h - 4)

        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0, BG_TOP)
        bg.setColorAt(1, BG_BOTTOM)
        border = QLinearGradient(0, 0, w, h)
        border.setColorAt(0, PURPLE)
        border.setColorAt(1, BLUE)
        p.setBrush(bg)
        p.setPen(QPen(border, 2 * k))
        p.drawRoundedRect(rect, 16 * k, 16 * k)

        pad = 16 * k
        left = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        right = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

        # title + status
        p.setFont(self._font(9, True, k))
        p.setPen(PURPLE)
        p.drawText(QRectF(pad, 10 * k, w / 2, 20 * k), left, "CHESTS OPENED")
        status = self._data["status"]
        p.setPen(BLUE if status == STATUS_WATCHING else (RED if status == STATUS_ERROR else MUTED))
        p.setFont(self._font(8, True, k))
        p.drawText(QRectF(w / 2, 10 * k, w / 2 - pad, 20 * k), right, status)

        # big match count
        p.setFont(self._font(38, True, k))
        p.setPen(WHITE)
        p.drawText(QRectF(pad, 28 * k, w - 2 * pad, 56 * k), left, str(self._data["match"]))

        # session + timer
        p.setFont(self._font(10, False, k))
        p.setPen(MUTED)
        p.drawText(QRectF(pad, h - 34 * k, w / 2, 22 * k), left, f"SESSION  {self._data['session']}")
        p.setPen(BLUE)
        p.drawText(QRectF(w / 2, h - 34 * k, w / 2 - pad, 22 * k), right, self._data["timer"])
        if self.locked:
            p.setFont(self._font(7, True, k))
            p.setPen(PURPLE)
            p.drawText(QRectF(0, h - 34 * k, w, 22 * k), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, "LOCKED")
        p.end()

    @staticmethod
    def _font(pt: float, bold: bool, k: float) -> QFont:
        f = QFont("Segoe UI")
        f.setPointSizeF(max(5.0, pt * k))
        f.setBold(bold)
        return f

    # ---- interaction ----------------------------------------------------
    def mousePressEvent(self, e) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e) -> None:
        if self._drag_offset is not None and (e.buttons() & Qt.MouseButton.LeftButton):
            self.move(e.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, e) -> None:
        if e.button() == Qt.MouseButton.LeftButton and self._drag_offset is not None:
            self._drag_offset = None
            self.moved.emit(self.x(), self.y())

    def contextMenuEvent(self, e) -> None:
        menu = QMenu(self)
        menu.addAction("Add chest (+1)", self.chest_added.emit)
        menu.addAction("Remove chest (-1)", self.chest_removed.emit)
        menu.addSeparator()
        menu.addAction("New match", self.new_match_requested.emit)
        if self.hotkeys_active:
            menu.addSeparator()
            menu.addAction("Hide overlay", self.hide_requested.emit)
            menu.addAction("Click-through (lock)", self.click_through_requested.emit)
        menu.addSeparator()
        menu.addAction("Quit", self.quit_requested.emit)
        menu.exec(e.globalPos())
