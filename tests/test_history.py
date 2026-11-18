import csv
import re

from app.config.settings import Settings
from app.core.controller import TrackerController
from app.core.sound import SoundPlayer
from app.database.db import Database
from app.ui.dashboard_model import best_flags, chests_label, export_filename, history_summary


def make(tmp_path):
    return TrackerController(Settings(), Database(tmp_path / "x.db"), SoundPlayer(tmp_path / "snd", False, player=None),
                             settings_path=tmp_path / "s.json", startup_setter=lambda on: None)


def match(started, chests):
    return {"started_at": started, "ended_at": started + 60, "duration_s": 60.0, "chests": chests, "events": []}


def test_all_matches_newest_first_and_not_limited():
    db = Database(":memory:")
    for i in range(30):
        db.save_match(match(1000.0 + i, i))
    rows = db.all_matches()
    assert len(rows) == 30 and rows[0]["chests"] == 29 and rows[-1]["chests"] == 0


def test_history_summary_text():
    db = Database(":memory:")
    assert history_summary(db.all_matches()) == "No finished matches yet."
    db.save_match(match(1.0, 1))
    assert history_summary(db.all_matches()) == "1 match, 1 chest in total"
    db.save_match(match(2.0, 4))
    assert history_summary(db.all_matches()) == "2 matches, 5 chests in total"


def test_export_filename_is_dated():
    assert re.fullmatch(r"chest_matches_\d{4}-\d{2}-\d{2}\.csv", export_filename(1_700_000_000.0))


def test_controller_export_writes_finished_matches_only(tmp_path):
    c = make(tmp_path)
    c.add(); c.add(); c.new_match()
    c.add()                                      # match in progress: must not be exported
    out = tmp_path / "o.csv"
    assert c.export_matches(out) == (1, None)
    rows = list(csv.reader(open(out, encoding="utf-8")))
    assert len(rows) == 2 and rows[1][-1] == "2"


def test_controller_export_reports_bad_path(tmp_path):
    c = make(tmp_path)
    count, error = c.export_matches(tmp_path / "missing_folder" / "o.csv")
    assert count == 0 and error and error.startswith("Could not write the file")


def test_best_flags_mark_best_and_ties_but_not_zero():
    db = Database(":memory:")
    assert best_flags(db.all_matches()) == []
    for i, n in enumerate((3, 7, 7, 1)):
        db.save_match(match(100.0 + i, n))
    assert best_flags(db.all_matches()) == [False, True, True, False]      # newest first: 1, 7, 7, 3
    db2 = Database(":memory:"); db2.save_match(match(1.0, 0))
    assert best_flags(db2.all_matches()) == [False]
    assert chests_label("7", True) == "\u2605 7" and chests_label("7", False) == "7"
