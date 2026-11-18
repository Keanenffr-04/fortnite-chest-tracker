from app.config.settings import Settings


def test_roundtrip(tmp_path):
    p = tmp_path / "s.json"
    s = Settings(); s.overlay_opacity = 0.5; s.save(p)
    assert Settings.load(p).overlay_opacity == 0.5


def test_bad_file_falls_back_to_defaults(tmp_path):
    p = tmp_path / "s.json"; p.write_text("{not json")
    assert Settings.load(p).detection_cooldown_s == 1.5


def test_values_clamped(tmp_path):
    s = Settings(); s.overlay_opacity = 9; s.detection_sensitivity = -3; s.validate()
    assert s.overlay_opacity == 1.0 and s.detection_sensitivity == 0.0


def test_unknown_keys_ignored(tmp_path):
    p = tmp_path / "s.json"; p.write_text('{"nope": 1, "overlay_scale": 2.0}')
    assert Settings.load(p).overlay_scale == 2.0
