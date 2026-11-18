"""Settings page. Widgets are generated from app.ui.settings_model.SECTIONS."""
from __future__ import annotations

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QFrame, QHBoxLayout, QLabel,
                               QLineEdit, QMessageBox, QPushButton, QScrollArea, QSlider, QSpinBox,
                               QVBoxLayout, QWidget)

from app.ui.settings_model import SECTIONS, SECTION_BLURBS, coerce, current_values, tooltip


class _Percent(QWidget):
    """Slider 0-100 % that maps to a float between field.minimum and field.maximum."""

    def __init__(self, field):
        super().__init__()
        self.f = field
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(round(field.minimum * 100), round(field.maximum * 100))
        self.label = QLabel("")
        self.label.setMinimumWidth(44)
        lay.addWidget(self.slider, 1)
        lay.addWidget(self.label)
        self.slider.valueChanged.connect(lambda v: self.label.setText(f"{v}%"))

    def value(self) -> float:
        return self.slider.value() / 100.0

    def set_value(self, v: float) -> None:
        self.slider.setValue(round(float(v) * 100))
        self.label.setText(f"{self.slider.value()}%")


class SettingsPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.setObjectName("page")
        self.ctl = controller
        self._w: dict[str, object] = {}      # key -> widget
        self._loaded: dict[str, object] = {}  # key -> value last pushed into the widget

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(10)
        title = QLabel("Settings")
        title.setObjectName("pageTitle")
        outer.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        body.setObjectName("page")
        self.body = QVBoxLayout(body)
        self.body.setSpacing(14)
        for section, fields_ in SECTIONS:
            self._add_section(section, fields_)
        self._add_data_section()
        self.body.addStretch(1)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        bar = QHBoxLayout()
        self.message = QLabel("")
        self.message.setWordWrap(True)
        self.message.setText("Changes take effect when you press Apply.")
        self.message.setObjectName("hint")
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.setObjectName("primary")
        self.btn_apply.setMinimumHeight(36)
        self.btn_reset = QPushButton("Reset to defaults")
        self.btn_reset.setToolTip("Puts every setting back to normal. Your statistics are not touched.")
        self.btn_reset.setMinimumHeight(36)
        bar.addWidget(self.message, 1)
        bar.addWidget(self.btn_reset)
        bar.addWidget(self.btn_apply)
        outer.addLayout(bar)

        self.btn_apply.clicked.connect(self.apply)
        self.btn_reset.clicked.connect(self.reset_settings)
        self.load(self.ctl.settings)

    # ---- building --------------------------------------------------------
    def _make_widget(self, f):
        if f.kind == "bool":
            return QCheckBox()
        if f.kind == "percent":
            return _Percent(f)
        if f.kind == "float":
            w = QDoubleSpinBox()
            w.setDecimals(2)
            w.setRange(f.minimum, f.maximum)
            w.setSingleStep(f.step)
            return w
        if f.kind == "int":
            w = QSpinBox()
            w.setRange(int(f.minimum), int(f.maximum))
            w.setSingleStep(int(f.step))
            return w
        if f.kind == "choice":
            w = QComboBox()
            for value, label in f.choices:
                w.addItem(label, value)
            return w
        w = QLineEdit()
        w.setPlaceholderText("e.g. ctrl+shift+o")
        return w

    def _card(self, name: str, blurb: str = ""):
        """A rounded card with a heading (and a one-line explanation); returns the card's layout."""
        card = QFrame()
        card.setObjectName("card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(6)
        head = QLabel(name)
        head.setObjectName("sectionTitle")
        head.setStyleSheet("margin-top: 0px;")
        lay.addWidget(head)
        if blurb:
            sub = QLabel(blurb)
            sub.setObjectName("muted")
            sub.setWordWrap(True)
            lay.addWidget(sub)
        self.body.addWidget(card)
        return lay

    def _add_section(self, name, fields_) -> None:
        lay = self._card(name, SECTION_BLURBS.get(name, ""))
        form = QFormLayout()
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(8)
        for f in fields_:
            w = self._make_widget(f)
            w.setToolTip(tooltip(f))
            self._w[f.key] = w
            if f.kind == "bool":
                w.setText(f.label)
                form.addRow(w)
            else:
                form.addRow(f.label, w)
            if f.hint:
                hint = QLabel(f.hint)
                hint.setObjectName("hint")
                hint.setWordWrap(True)
                form.addRow("", hint)
        if name == "Sound":
            test = QPushButton("Play test sound")
            test.setToolTip("Plays the chime at the SAVED volume. Press Apply first to hear changes.")
            test.clicked.connect(self._test_sound)
            form.addRow("", test)
        lay.addLayout(form)

    def _add_data_section(self) -> None:
        lay = self._card("Data", "Your matches and settings live in one folder on this PC.")
        self.data_dir = QLabel("")
        self.data_dir.setObjectName("hint")
        self.data_dir.setWordWrap(True)
        self.data_dir.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(self.data_dir)
        row = QHBoxLayout()
        btn_open = QPushButton("Open data folder")
        btn_open.setToolTip("Opens the folder in Explorer.")
        btn_open.clicked.connect(self._open_data_dir)
        btn_wipe = QPushButton("Reset statistics...")
        btn_wipe.setObjectName("danger")
        btn_wipe.setToolTip("Deletes all saved matches. Asks you to confirm first.")
        btn_wipe.clicked.connect(self.reset_statistics)
        row.addWidget(btn_open)
        row.addWidget(btn_wipe)
        row.addStretch(1)
        lay.addLayout(row)

    # ---- widget <-> value ------------------------------------------------
    def _get(self, f):
        w = self._w[f.key]
        if f.kind == "bool":
            return w.isChecked()
        if f.kind == "percent":
            return w.value()
        if f.kind in ("float", "int"):
            return w.value()
        if f.kind == "choice":
            return w.currentData()
        return w.text()

    def _set(self, f, value) -> None:
        w = self._w[f.key]
        if f.kind == "bool":
            w.setChecked(bool(value))
        elif f.kind == "percent":
            w.set_value(value)
        elif f.kind in ("float", "int"):
            w.setValue(value)
        elif f.kind == "choice":
            idx = w.findData(value)
            w.setCurrentIndex(max(0, idx))
        else:
            w.setText(str(value))

    def _fields(self):
        return [f for _, fs in SECTIONS for f in fs]

    def collect(self) -> dict:
        return {f.key: coerce(f, self._get(f)) for f in self._fields()}

    def load(self, settings) -> None:
        """Push settings into the widgets. Only widgets whose setting actually changed are touched,
        so something you are half-way through typing is not wiped by an unrelated change."""
        values = current_values(settings)
        for f in self._fields():
            if self._loaded.get(f.key, object()) != values[f.key]:
                self._set(f, values[f.key])
                self._loaded[f.key] = values[f.key]
        self.data_dir.setText(settings.data_dir)

    # ---- actions ---------------------------------------------------------
    def _say(self, text: str, ok: bool) -> None:
        self.message.setObjectName("ok" if ok else "problem")
        self.message.style().unpolish(self.message)
        self.message.style().polish(self.message)
        self.message.setText(text)

    def apply(self) -> None:
        problems, warnings = self.ctl.apply_changes(self.collect())
        if problems:
            self._say("Not saved:  " + "   |   ".join(problems), ok=False)
            return
        self.load(self.ctl.settings)       # show what was really stored (clamped, reverted...)
        self._say("Saved." + ("  " + "  ".join(warnings) if warnings else ""), ok=not warnings)

    def reset_settings(self) -> None:
        if QMessageBox.question(self, "Reset settings",
                                "Reset all settings to their defaults?\n"
                                "Your statistics are not affected.") != QMessageBox.StandardButton.Yes:
            return
        warnings = self.ctl.reset_settings()
        self.load(self.ctl.settings)
        self._say("Settings reset." + ("  " + "  ".join(warnings) if warnings else ""), ok=not warnings)

    def reset_statistics(self) -> None:
        if QMessageBox.question(self, "Reset statistics",
                                "Permanently delete ALL saved matches and chest history?\n"
                                "This cannot be undone. (Settings and the match in progress are kept.)",
                                defaultButton=QMessageBox.StandardButton.No
                                ) != QMessageBox.StandardButton.Yes:
            return
        self.ctl.reset_statistics()
        self._say("Statistics deleted.", ok=True)

    def _test_sound(self) -> None:
        # Plays with the SAVED volume/enabled state, so press Apply first to hear changes.
        if not self.ctl.sound.play_up():
            self._say("No sound played (sound is off, or not on Windows).", ok=False)

    def _open_data_dir(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.ctl.settings.data_dir))
