from app.core.counter import ChestCounter
from app.overlay.model import (BASE_H, BASE_W, STATUS_MANUAL, clamp_position,
                               format_timer, scaled_size, snapshot)


def test_format_timer():
    assert format_timer(0) == "00:00"
    assert format_timer(65) == "01:05"
    assert format_timer(3599) == "59:59"
    assert format_timer(3600) == "1:00:00"
    assert format_timer(-5) == "00:00"


def test_scaled_size_and_clamp_of_scale():
    assert scaled_size(1.0) == (BASE_W, BASE_H)
    assert scaled_size(2.0) == (BASE_W * 2, BASE_H * 2)
    assert scaled_size(99) == scaled_size(3.0)
    assert scaled_size(0.01) == scaled_size(0.5)


def test_clamp_position_keeps_overlay_on_screen():
    assert clamp_position(20, 20, 260, 124, 1920, 1080) == (20, 20)
    assert clamp_position(5000, 5000, 260, 124, 1920, 1080) == (1660, 956)
    assert clamp_position(-50, -10, 260, 124, 1920, 1080) == (0, 0)


def test_snapshot_reads_counter():
    t = [0.0]
    c = ChestCounter(0.8, 1.0, clock=lambda: t[0])
    c.manual_adjust(1); c.manual_adjust(1)
    t[0] = 75
    s = snapshot(c)
    assert s == {"match": 2, "session": 2, "timer": "01:15", "status": STATUS_MANUAL}


def test_footer_hidden_makes_overlay_shorter():
    from app.overlay.model import BASE_H_NO_FOOTER
    assert scaled_size(1.0, footer=False) == (BASE_W, BASE_H_NO_FOOTER)
    assert scaled_size(1.0, footer=False)[1] < scaled_size(1.0)[1]


def test_theme_names_match_between_settings_and_model():
    from app.config.settings import THEME_NAMES
    from app.overlay.model import THEMES
    assert set(THEME_NAMES) == set(THEMES)


def test_apply_option_sets_and_clamps():
    from app.config.settings import Settings
    from app.overlay.model import apply_option, options_from_settings
    st = Settings()
    apply_option(st, "opacity", 0.6); apply_option(st, "scale", 99); apply_option(st, "theme", "blue")
    apply_option(st, "show_timer", False); apply_option(st, "sound_enabled", False)
    o = options_from_settings(st)
    assert o["opacity"] == 0.6 and o["scale"] == 3.0 and o["theme"] == "blue"
    assert o["show_timer"] is False and o["sound_enabled"] is False


def test_apply_option_rejects_bad_input():
    from app.config.settings import Settings
    from app.overlay.model import apply_option
    st = Settings()
    for key, val in [("nope", 1), ("theme", "pink")]:
        try:
            apply_option(st, key, val)
        except ValueError:
            continue
        raise AssertionError(f"{key}={val} should have been rejected")
    assert st.overlay_theme == "violet"


def test_old_settings_file_without_new_keys_still_loads(tmp_path):
    from app.config.settings import Settings
    p = tmp_path / "s.json"
    p.write_text('{"overlay_x": 50, "overlay_theme": "garbage", "sound_volume": 7}')
    s = Settings.load(p)
    assert s.overlay_x == 50 and s.overlay_theme == "violet" and s.sound_volume == 1.0 and s.overlay_show_timer is True
