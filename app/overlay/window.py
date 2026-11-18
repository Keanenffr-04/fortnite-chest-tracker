"""The floating overlay window (PySide6). Custom-painted: dark, rounded, two accent colours.

Right-click for: add / remove chest, new match, opacity, size, theme, what to show, sound, quit.
Drag with the left mouse button to move it; the position is saved.
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QMenu, QWidget

from app.overlay.model import (OPACITY_PRESETS, SIZE_PRESETS, STATUS_ERROR, STATUS_MANUAL,
                               STATUS_WATCHING, THEMES, scaled_size)

BG_TOP = QColor(24, 20, 44)
BG_BOTTOM = QColor(12, 12, 24)
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
    option_changed = Signal(str, object)   # (option key, new value)

    def __init__(self, options: dict):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._data = {"match": 0, "session": 0, "timer": "00:00", "status": STATUS_MANUAL}
        self._drag_offset = None
        self.locked = False            # click-through on
        self.hotkeys_active = False    # hide/lock menu items only appear if hotkeys can undo them
        self._o = dict(options)
        self.apply_options(options)

    # ---- options --------------------------------------------------------
    def apply_options(self, options: dict) -> None:
        self._o = dict(options)
        footer = self._o["show_session"] or self._o["show_timer"]
        w, h = scaled_size(self._o["scale"], footer)
        self.setFixedSize(w, h)
        self.setWindowOpacity(min(1.0, max(0.1, self._o["opacity"])))
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
        o = self._o
        k = o["scale"]
        a1 = QColor(*THEMES.get(o["theme"], THEMES["violet"])[0])
        a2 = QColor(*THEMES.get(o["theme"], THEMES["violet"])[1])
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        rect = QRectF(2, 2, w - 4, h - 4)

        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0, BG_TOP)
        bg.setColorAt(1, BG_BOTTOM)
        border = QLinearGradient(0, 0, w, h)
        border.setColorAt(0, a1)
        border.setColorAt(1, a2)
        p.setBrush(bg)
        p.setPen(QPen(border, 2 * k))
        p.drawRoundedRect(rect, 16 * k, 16 * k)

        pad = 16 * k
        left = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        right = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

        # title (+ status)
        p.setFont(self._font(9, True, k))
        p.setPen(a1)
        p.drawText(QRectF(pad, 10 * k, w / 2, 20 * k), left, "CHESTS OPENED")
        if o["show_status"]:
            status = self._data["status"]
            p.setPen(a2 if status == STATUS_WATCHING else (RED if status == STATUS_ERROR else MUTED))
            p.setFont(self._font(8, True, k))
            p.drawText(QRectF(w / 2, 10 * k, w / 2 - pad, 20 * k), right, status)

        # big match count
        p.setFont(self._font(38, True, k))
        p.setPen(WHITE)
        p.drawText(QRectF(pad, 28 * k, w - 2 * pad, 56 * k), left, str(self._data["match"]))

        # footer: session + timer
        if o["show_session"] or o["show_timer"]:
            y = h - 34 * k
            p.setFont(self._font(10, False, k))
            if o["show_session"]:
                p.setPen(MUTED)
                p.drawText(QRectF(pad, y, w / 2, 22 * k), left, f"SESSION  {self._data['session']}")
            if o["show_timer"]:
                p.setPen(a2)
                p.drawText(QRectF(w / 2, y, w / 2 - pad, 22 * k), right, self._data["timer"])
            if self.locked:
                p.setFont(self._font(7, True, k))
                p.setPen(a1)
                p.drawText(QRectF(0, y, w, 22 * k),
                           Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, "LOCKED")
        elif self.locked:
            p.setFont(self._font(7, True, k))
            p.setPen(a1)
            p.drawText(QRectF(0, h - 26 * k, w, 16 * k),
                       Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, "LOCKED")
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

    def _choice(self, menu, text, key, value, checked) -> None:
        act = menu.addAction(text)
        act.setCheckable(True)
        act.setChecked(checked)
        act.triggered.connect(lambda _=False, k=key, v=value: self.option_changed.emit(k, v))

    def _toggle(self, menu, text, key) -> None:
        act = menu.addAction(text)
        act.setCheckable(True)
        act.setChecked(bool(self._o[key]))
        act.triggered.connect(lambda checked=False, k=key: self.option_changed.emit(k, bool(checked)))

    def contextMenuEvent(self, e) -> None:
        o = self._o
        menu = QMenu(self)
        menu.addAction("Add chest (+1)", self.chest_added.emit)
        menu.addAction("Remove chest (-1)", self.chest_removed.emit)
        menu.addSeparator()
        menu.addAction("New match", self.new_match_requested.emit)
        menu.addSeparator()

        sub = menu.addMenu("Opacity")
        for v in OPACITY_PRESETS:
            self._choice(sub, f"{round(v * 100)}%", "opacity", v, abs(o["opacity"] - v) < 0.05)
        sub = menu.addMenu("Size")
        for name, v in SIZE_PRESETS.items():
            self._choice(sub, name, "scale", v, abs(o["scale"] - v) < 0.05)
        sub = menu.addMenu("Theme")
        for name in THEMES:
            self._choice(sub, name.capitalize(), "theme", name, o["theme"] == name)
        sub = menu.addMenu("Show")
        self._toggle(sub, "Status", "show_status")
        self._toggle(sub, "Session count", "show_session")
        self._toggle(sub, "Match timer", "show_timer")
        self._toggle(menu, "Sound", "sound_enabled")

        if self.hotkeys_active:
            menu.addSeparator()
            menu.addAction("Hide overlay", self.hide_requested.emit)
            menu.addAction("Click-through (lock)", self.click_through_requested.emit)
        menu.addSeparator()
        menu.addAction("Quit", self.quit_requested.emit)
        menu.exec(e.globalPos())
