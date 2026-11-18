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
    print(f"Fortnite Chest Tracker {__version__}: self-test passed (synthetic data only).")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Fortnite Live Chest Tracker")
    p.add_argument("--version", action="store_true")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--record", action="store_true", help="record chest samples with hotkeys")
    p.add_argument("--benchmark", action="store_true", help="measure screen capture speed")
    a = p.parse_args()
    if a.version:
        print(__version__); return 0
    if a.selftest:
        return selftest()
    if a.record:
        from app.capture.tool import run_record
        return run_record()
    if a.benchmark:
        from app.capture.tool import run_benchmark
        return run_benchmark()
    print(f"Fortnite Chest Tracker {__version__}\n"
          "Chest detection, overlay and dashboard are NOT built yet (see ROADMAP.md).\n"
          "Run with --selftest to verify the core logic,\n"
          "--benchmark to measure screen capture, --record to collect chest samples.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
