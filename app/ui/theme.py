"""Dark theme with purple/blue cards. Accent colours follow the overlay theme setting.
Returns a Qt style sheet string (plain text, so it is unit-tested without Qt)."""
from __future__ import annotations

from app.overlay.model import THEMES

BG = "#0f0d1f"
PANEL = "#15122b"
CARD = "#1b1738"
BORDER = "#2b2552"
TEXT = "#f5f5ff"
MUTED = "#a0a0be"


def _hex(rgb) -> str:
    return "#%02x%02x%02x" % tuple(rgb)


_TEMPLATE = """
* { font-family: "Segoe UI", sans-serif; font-size: 10pt; color: @TEXT@; }
QMainWindow, QWidget#page, QStackedWidget { background: @BG@; }
QWidget#sidebar { background: @PANEL@; border-right: 1px solid @BORDER@; }
QLabel#appTitle { font-size: 13pt; font-weight: bold; color: @A1@; }
QLabel#pageTitle { font-size: 18pt; font-weight: bold; }
QLabel#sectionTitle { font-size: 11pt; font-weight: bold; color: @A1@; margin-top: 8px; }
QLabel#muted, QLabel#hint, QLabel#cardLabel { color: @MUTED@; }
QLabel#hint { font-size: 8.5pt; }
QLabel#cardValue { font-size: 26pt; font-weight: bold; }
QLabel#bigCount { font-size: 72pt; font-weight: bold; }
QLabel#status { color: @A2@; font-weight: bold; }
QLabel#problem { color: #ef4444; }
QLabel#ok { color: #22c55e; }
QLabel#banner { background: @CARD@; border: 1px solid @A2@; border-radius: 10px; padding: 10px; color: @MUTED@; }
QFrame#card { background: @CARD@; border: 1px solid @BORDER@; border-radius: 14px; }
QPushButton { background: @CARD@; border: 1px solid @BORDER@; border-radius: 8px; padding: 8px 14px; }
QPushButton:hover { border-color: @A1@; }
QPushButton:disabled { color: @MUTED@; }
QPushButton#primary { border: none; font-weight: bold;
  background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 @A1@, stop:1 @A2@); }
QPushButton#danger { border: 1px solid #ef4444; color: #ef4444; }
QPushButton#nav { text-align: left; border: none; border-radius: 8px; padding: 10px 14px; background: transparent; }
QPushButton#nav:hover { background: @CARD@; }
QPushButton#nav:checked { background: @CARD@; border-left: 3px solid @A1@; font-weight: bold; }
QTableWidget, QListWidget { background: @CARD@; border: 1px solid @BORDER@; border-radius: 10px; gridline-color: @BORDER@; }
QHeaderView::section { background: @PANEL@; border: none; padding: 6px; color: @MUTED@; }
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; border: 1px solid @BORDER@; background: @CARD@; }
QCheckBox::indicator:checked { background: @A1@; border-color: @A1@; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox { background: @CARD@; border: 1px solid @BORDER@; border-radius: 6px; padding: 5px 8px; }
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus { border-color: @A1@; }
QSlider::groove:horizontal { height: 6px; background: @BORDER@; border-radius: 3px; }
QSlider::sub-page:horizontal { background: @A1@; border-radius: 3px; }
QSlider::handle:horizontal { width: 16px; margin: -5px 0; border-radius: 8px; background: @A2@; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { background: @PANEL@; width: 10px; }
QScrollBar::handle:vertical { background: @BORDER@; border-radius: 5px; min-height: 24px; }
"""


def stylesheet(theme: str = "violet") -> str:
    a1, a2 = THEMES.get(theme, THEMES["violet"])
    tokens = {"@A1@": _hex(a1), "@A2@": _hex(a2), "@BG@": BG, "@PANEL@": PANEL,
              "@CARD@": CARD, "@BORDER@": BORDER, "@TEXT@": TEXT, "@MUTED@": MUTED}
    css = _TEMPLATE
    for token, value in tokens.items():
        css = css.replace(token, value)
    return css
