from dataclasses import fields

from app.config.settings import THEME_NAMES, Settings
from app.overlay.hotkey_map import ACTIONS
from app.ui.settings_model import (FIELDS, SECTIONS, apply_changes, coerce,
                                   current_values, defaults_keeping)


def test_every_field_is_a_real_setting_with_sane_defaults():
    s = Settings()
    names = {f.name for f in fields(Settings)}
    for key, f in FIELDS.items():
        assert key in names, key
        v = getattr(s, key)
        if f.kind in ("percent", "float", "int"):
            assert f.minimum <= v <= f.maximum, (key, v)
        if f.kind == "choice":
            assert v in [c for c, _ in f.choices], key
        if f.kind == "bool":
            assert isinstance(v, bool), key


def test_all_hotkeys_and_themes_are_on_the_page():
    for attr in ACTIONS.values():
        assert attr in FIELDS
    theme = FIELDS["overlay_theme"]
    assert [v for v, _ in theme.choices] == list(THEME_NAMES)
    assert len({k for _, fs in SECTIONS for k in (f.key for f in fs)}) == len(FIELDS)  # no duplicates


def test_current_values_roundtrip_is_a_noop():
    s = Settings()
    new, problems = apply_changes(s, current_values(s))
    assert problems == [] and new == s


def test_valid_change_applies_to_copy_only():
    s = Settings()
    new, problems = apply_changes(s, {"overlay_opacity": 0.5, "hotkey_quit": " Ctrl+Alt+Q "})
    assert problems == [] and new.overlay_opacity == 0.5 and new.hotkey_quit == " Ctrl+Alt+Q ".strip()
    assert s.overlay_opacity == 0.85           # original untouched


def test_values_are_clamped_by_validate():
    new, _ = apply_changes(Settings(), {"overlay_opacity": 5, "overlay_scale": 0.01})
    assert new.overlay_opacity == 1.0 and new.overlay_scale == 0.5


def test_bad_values_rejected():
    for changes in ({"overlay_theme": "pink"}, {"detection_interval_ms": "abc"},
                    {"nope": 1}, {"sound_volume": None}):
        new, problems = apply_changes(Settings(), changes)
        assert new is None and problems, changes


def test_hotkey_rules_enforced():
    for hk in ("a", "ctrl"):
        new, problems = apply_changes(Settings(), {"hotkey_add_chest": hk})
        assert new is None and problems, hk
    new, problems = apply_changes(Settings(), {"hotkey_add_chest": ""})   # empty = disabled
    assert problems == [] and new.hotkey_add_chest == ""


def test_coerce_kinds():
    assert coerce(FIELDS["overlay_visible"], 1) is True
    assert coerce(FIELDS["detection_interval_ms"], "50") == 50
    assert coerce(FIELDS["overlay_scale"], "1.5") == 1.5


def test_defaults_keeping():
    s = Settings()
    s.overlay_theme, s.data_dir, s.overlay_x, s.overlay_y = "red", "D:/x", 9, 8
    d = defaults_keeping(s)
    assert d.overlay_theme == "violet" and d.data_dir == "D:/x" and (d.overlay_x, d.overlay_y) == (9, 8)
