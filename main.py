"""Fortnite Live Chest Tracker - entry point."""
import argparse
import sys
import tempfile
from pathlib import Path

from app import __version__


def selftest() -> int:
    """Exercise counter + database + settings with synthetic data. Does NOT test Fortnite detection."""
    from app.config.settings import Settings
    from app.core.counter import ChestCounter
    from app.database.db import Database

    t = [0.0]
    c = ChestCounter(sensitivity=0.8, cooldown_s=1.5, clock=lambda: t[0])
    assert c.register_detection(0.95)
    assert not c.register_detection(0.95)      # duplicate inside cooldown
    t[0] += 2.0
    assert c.register_detection(0.95)
    assert not c.register_detection(0.40)      # below sensitivity
    with tempfile.TemporaryDirectory() as d:
        db = Database(Path(d) / "t.db")
        db.save_match(c.new_match())
        assert db.total_chests() == 2
        db.close()
        s = Settings(); s.save(Path(d) / "s.json"); Settings.load(Path(d) / "s.json")
        from app.core.controller import TrackerController
        from app.core.sound import SoundPlayer
        ctl = TrackerController(Settings(), Database(Path(d) / "c.db"), SoundPlayer(Path(d) / "snd", False, player=None),
                                settings_path=Path(d) / "c.json", startup_setter=lambda on: None)
        ctl.add(); ctl.add(); ctl.new_match()
        assert ctl.stats()["total"] == 2
        assert ctl.apply_changes({"overlay_theme": "blue"}) == ([], [])
        ctl.finish()
    print(f"Fortnite Chest Tracker {__version__}: self-test passed (synthetic data only).")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Fortnite Live Chest Tracker")
    p.add_argument("--version", action="store_true")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--record", action="store_true", help="record chest samples with hotkeys")
    p.add_argument("--app", action="store_true", help="open the main window (dashboard) + overlay")
    p.add_argument("--overlay", action="store_true", help="show only the live overlay (manual counting for now)")
    p.add_argument("--benchmark", action="store_true", help="measure screen capture speed")
    p.add_argument("--detect-debug", metavar="FOLDER", help="run the detector on recorded samples and save annotated frames")
    p.add_argument("--make-template", nargs=6, metavar=("FRAME", "NAME", "X", "Y", "W", "H"),
                   help="cut a reference template out of a sample frame (X Y W H = fractions 0-1)")
    a = p.parse_args()
    if a.version:
        print(__version__); return 0
    if a.selftest:
        return selftest()
    if a.record:
        from app.capture.tool import run_record
        return run_record()
    if a.app:
        from app.overlay.runner import run_app
        return run_app()
    if a.overlay:
        from app.overlay.runner import run_overlay
        return run_overlay()
    if a.benchmark:
        from app.capture.tool import run_benchmark
        return run_benchmark()
    if a.detect_debug:
        from app.detect.debug import run_detect_debug
        return run_detect_debug(a.detect_debug)
    if a.make_template:
        from app.detect.debug import run_make_template
        frame, name, x, y, w, h = a.make_template
        try:
            box = [float(v) for v in (x, y, w, h)]
        except ValueError:
            print("X Y W H must be numbers between 0 and 1"); return 1
        return run_make_template(frame, name, *box)
    print(f"Fortnite Chest Tracker {__version__}\n"
          "Automatic counting is NOT switched on yet: the detection engine exists (--detect-debug) but is not wired in (see ROADMAP.md).\n"
          "Run with --app for the dashboard + overlay, --overlay for the overlay only,\n"
          "--selftest to verify the core logic, --benchmark to measure capture, --record to collect samples,\n"
          "--make-template / --detect-debug to build and test detection templates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
