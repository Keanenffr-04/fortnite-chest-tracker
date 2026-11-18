"""Small reusable widgets (PySide6)."""
from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class Card(QFrame):
    """A rounded stat card: small label on top, big value below."""

    def __init__(self, label: str, value: str = "0"):
        super().__init__()
        self.setObjectName("card")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(2)
        self._label = QLabel(label)
        self._label.setObjectName("cardLabel")
        self._value = QLabel(value)
        self._value.setObjectName("cardValue")
        lay.addWidget(self._label)
        lay.addWidget(self._value)

    def set_label(self, text: str) -> None:
        self._label.setText(text)

    def set_value(self, text: str) -> None:
        self._value.setText(text)
