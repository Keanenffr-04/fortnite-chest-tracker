from app.config.settings import Settings
from app.overlay.hotkey_map import build_bindings, check, normalise


def test_normalise():
    assert normalise(" Ctrl + Shift + O ") == "ctrl+shift+o"
    assert normalise("Control+Win+x") == "ctrl+windows+x"
    assert normalise("") == ""


def test_check_rules():
    assert check("ctrl+shift+o") is None
    assert check("f8") is None                 # function keys are fine alone
    assert check("") is None                   # disabled
    assert check("w") is not None              # bare letter would fire while playing
    assert check("ctrl+shift") is not None     # no real key
    assert check("5") is not None


def test_default_settings_give_five_valid_bindings():
    b, problems = build_bindings(Settings())
    assert problems == []
    assert set(b) == {"toggle_overlay", "add_chest", "remove_chest", "toggle_click_through", "quit"}


def test_duplicates_and_bad_keys_are_reported_and_left_out():
    s = Settings()
    s.hotkey_quit = "ctrl+shift+o"    # same as toggle_overlay
    s.hotkey_add_chest = "w"          # unsafe
    s.hotkey_remove_chest = ""        # disabled on purpose
    b, problems = build_bindings(s)
    assert "toggle_overlay" in b and "quit" not in b
    assert "add_chest" not in b and "remove_chest" not in b
    assert len(problems) == 2


def test_new_settings_roundtrip(tmp_path):
    s = Settings(); s.hotkey_quit = "ctrl+alt+q"; s.save(tmp_path / "s.json")
    assert Settings.load(tmp_path / "s.json").hotkey_quit == "ctrl+alt+q"
