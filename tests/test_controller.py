from app.config.settings import Settings
from app.core.controller import TrackerController
from app.core.sound import SoundPlayer
from app.database.db import Database


def make(tmp_path, startup=None):
    played = []
    sound = SoundPlayer(tmp_path / "snd", True, 0.5, player=played.append)
    calls = []
    def fake_startup(on):
        calls.append(on)
        return startup(on) if startup else None
    c = TrackerController(Settings(), Database(tmp_path / "x.db"), sound,
                          settings_path=tmp_path / "s.json", startup_setter=fake_startup)
    return c, played, calls


def test_add_remove_play_sounds_and_notify(tmp_path):
    c, played, _ = make(tmp_path)
    kinds = []
    c.subscribe(kinds.append)
    c.add(); c.add(); c.remove()
    assert c.counter.match_count == 1
    assert [p.name for p in played] == ["chest_up.wav", "chest_up.wav", "chest_down.wav"]
    assert kinds == ["count", "count", "count"]


def test_remove_at_zero_is_silent_and_never_negative(tmp_path):
    c, played, _ = make(tmp_path)
    c.remove()
    assert c.counter.match_count == 0 and played == []


def test_new_match_saves_only_non_empty(tmp_path):
    c, _, _ = make(tmp_path)
    assert c.new_match() is None
    assert c.db.total_matches() == 0
    c.add(); c.add()
    assert c.new_match() is not None
    assert c.db.total_chests() == 2 and c.counter.match_count == 0
    assert c.counter.session_count == 2          # session total survives the match


def test_stats_include_live_match(tmp_path):
    c, _, _ = make(tmp_path)
    c.add(); c.add(); c.new_match()
    c.add()
    s = c.stats()
    assert (s["match"], s["total"], s["matches"], s["best"]) == (1, 3, 2, 2)


def test_listener_error_does_not_break_counting(tmp_path):
    c, _, _ = make(tmp_path)
    def boom(kind): raise RuntimeError("ui bug")
    c.subscribe(boom)
    c.add()
    assert c.counter.match_count == 1


def test_apply_changes_saves_syncs_and_notifies(tmp_path):
    c, _, _ = make(tmp_path)
    kinds = []
    c.subscribe(kinds.append)
    problems, warnings = c.apply_changes({"overlay_theme": "green", "detection_sensitivity": 0.6,
                                          "detection_cooldown_s": 3.0, "sound_volume": 0.2})
    assert problems == [] and warnings == []
    assert c.settings.overlay_theme == "green"
    assert c.counter.sensitivity == 0.6 and c.counter.cooldown_s == 3.0
    assert c.sound.volume == 0.2
    assert kinds == ["settings"]
    assert Settings.load(tmp_path / "s.json").overlay_theme == "green"


def test_apply_changes_is_all_or_nothing(tmp_path):
    c, _, _ = make(tmp_path)
    before = c.settings.overlay_theme
    problems, _ = c.apply_changes({"overlay_theme": "red", "hotkey_add_chest": "x"})
    assert problems and c.settings.overlay_theme == before


def test_duplicate_hotkeys_rejected(tmp_path):
    c, _, _ = make(tmp_path)
    problems, _ = c.apply_changes({"hotkey_quit": "ctrl+shift+o"})
    assert problems and "already used" in problems[0]
    assert c.settings.hotkey_quit == "ctrl+shift+q"


def test_start_with_windows_success_and_failure(tmp_path):
    c, _, calls = make(tmp_path)
    assert c.apply_changes({"start_with_windows": True}) == ([], [])
    assert c.settings.start_with_windows is True and calls == [True]

    c2, _, _ = make(tmp_path, startup=lambda on: "no registry")
    problems, warnings = c2.apply_changes({"start_with_windows": True, "overlay_theme": "blue"})
    assert problems == [] and warnings == ["no registry"]
    assert c2.settings.start_with_windows is False       # reverted to the truth
    assert c2.settings.overlay_theme == "blue"           # the rest still applied


def test_startup_not_touched_when_unchanged(tmp_path):
    c, _, calls = make(tmp_path)
    c.apply_changes({"overlay_theme": "blue"})
    assert calls == []


def test_set_option_from_overlay_menu(tmp_path):
    c, _, _ = make(tmp_path)
    c.set_option("opacity", 0.6)
    c.set_option("theme", "nonsense")          # ignored, no crash
    assert c.settings.overlay_opacity == 0.6 and c.settings.overlay_theme == "violet"
    c.set_option("sound_enabled", False)
    assert c.sound.enabled is False


def test_reset_settings_keeps_data_dir_and_position(tmp_path):
    c, _, calls = make(tmp_path)
    c.apply_changes({"overlay_theme": "red", "start_with_windows": True})
    c.settings.data_dir = "D:/keep"
    c.set_overlay_position(300, 400)
    c.reset_settings()
    assert c.settings.overlay_theme == "violet" and c.settings.start_with_windows is False
    assert c.settings.data_dir == "D:/keep"
    assert (c.settings.overlay_x, c.settings.overlay_y) == (300, 400)
    assert calls == [True, False]


def test_visibility_click_through_position_persist(tmp_path):
    c, _, _ = make(tmp_path)
    kinds = []
    c.subscribe(kinds.append)
    c.set_overlay_visible(False); c.set_click_through(True); c.set_overlay_position(5, 6)
    s = Settings.load(tmp_path / "s.json")
    assert (s.overlay_visible, s.overlay_click_through, s.overlay_x, s.overlay_y) == (False, True, 5, 6)
    assert kinds == ["settings", "settings"]     # position does not notify


def test_reset_statistics_keeps_live_match(tmp_path):
    c, _, _ = make(tmp_path)
    c.add(); c.new_match(); c.add()
    kinds = []
    c.subscribe(kinds.append)
    c.reset_statistics()
    assert c.db.total_matches() == 0 and c.counter.match_count == 1
    assert kinds == ["reset"]
    c.add(); c.new_match()                       # saving after a reset still works
    assert c.db.total_chests() == 2


def test_finish_saves_match_and_closes(tmp_path):
    c, _, _ = make(tmp_path)
    c.add()
    path = c.db.path
    c.finish()
    db = Database(path)
    assert db.total_chests() == 1
    assert db.conn.execute("SELECT ended_at FROM sessions").fetchone()[0] is not None
    db.close()
