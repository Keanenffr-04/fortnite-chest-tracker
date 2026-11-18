from pathlib import Path
from types import SimpleNamespace

from app.core import launcher


def test_missing_modules_lists_only_what_is_absent():
    assert set(launcher.missing_modules(lambda m: None if m in ("mss", "cv2") else object())) == {"mss", "cv2"}
    assert launcher.missing_modules(lambda m: object()) == []


def test_console_python_swaps_pythonw(tmp_path):
    (tmp_path / "python.exe").write_text(""); (tmp_path / "pythonw.exe").write_text("")
    assert launcher.console_python(str(tmp_path / "pythonw.exe")).endswith("python.exe")
    assert launcher.console_python(str(tmp_path / "other.exe")).endswith("other.exe")


def test_install_reports_failure_and_start_error():
    bad = lambda *a, **k: SimpleNamespace(returncode=1, stdout="", stderr="no internet\nboom")
    assert "boom" in launcher.install_requirements(Path("r.txt"), "py", run=bad)
    ok = lambda *a, **k: SimpleNamespace(returncode=0, stdout="", stderr="")
    assert launcher.install_requirements(Path("r.txt"), "py", run=ok) is None

    def boom(*a, **k): raise OSError("nope")
    assert "nope" in launcher.install_requirements(Path("r.txt"), "py", run=boom)


def test_launch_defaults_to_app_and_skips_install_when_nothing_missing():
    seen, msgs = {}, []
    def entry():
        import sys; seen["argv"] = list(sys.argv); return 0
    rc = launcher.launch([], find=lambda m: object(), installer=lambda r: msgs.append("installed"),
                         notify=lambda t, error=False: msgs.append(t), entry=entry)
    assert rc == 0 and seen["argv"] == ["main.py", "--app"] and msgs == []
    launcher.launch(["--overlay"], find=lambda m: object(), notify=lambda *a, **k: None, entry=entry)
    assert seen["argv"] == ["main.py", "--overlay"]


def test_launch_installs_then_runs_and_reports_failures():
    state, msgs = {"have": False}, []
    find = lambda m: object() if state["have"] else None
    def installer(req): state["have"] = True; return None
    rc = launcher.launch(["--selftest"], find=find, installer=installer,
                         notify=lambda t, error=False: msgs.append((t, error)), entry=lambda: 0)
    assert rc == 0 and len(msgs) == 1 and not msgs[0][1]          # one "installing" notice, not an error
    msgs.clear()
    rc = launcher.launch([], find=lambda m: None, installer=lambda r: "pip failed",
                         notify=lambda t, error=False: msgs.append((t, error)), entry=lambda: 0)
    assert rc == 1 and msgs[-1][1] and "pip failed" in msgs[-1][0]


def test_launch_shows_crash_in_message_box():
    msgs = []
    def entry(): raise RuntimeError("kaboom")
    rc = launcher.launch([], find=lambda m: object(), notify=lambda t, error=False: msgs.append((t, error)), entry=entry)
    assert rc == 1 and msgs[0][1] and "kaboom" in msgs[0][0]
