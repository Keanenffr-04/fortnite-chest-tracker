from pathlib import Path

from app.core import startup


class FakeReg:
    def __init__(self, fail=False):
        self.value, self.fail = None, fail
    def get(self): return self.value
    def set(self, cmd):
        if self.fail: raise PermissionError("denied")
        self.value = cmd
    def delete(self):
        if self.fail: raise PermissionError("denied")
        self.value = None


def test_enable_disable_roundtrip():
    r = FakeReg()
    assert startup.is_enabled(r) is False
    assert startup.set_enabled(True, r, command="cmd") is None
    assert r.value == "cmd" and startup.is_enabled(r) is True
    assert startup.set_enabled(False, r) is None
    assert startup.is_enabled(r) is False


def test_registry_error_is_reported_not_raised():
    err = startup.set_enabled(True, FakeReg(fail=True), command="c")
    assert err and "denied" in err


def test_no_registry_means_not_windows():
    assert "only available on Windows" in startup.set_enabled(True, None)
    assert startup.is_enabled(None) is False


def test_startup_command_prefers_pythonw_and_overlay_only(tmp_path):
    (tmp_path / "python.exe").write_text("")
    (tmp_path / "pythonw.exe").write_text("")
    cmd = startup.startup_command(Path("C:/app/main.py"), str(tmp_path / "python.exe"))
    assert "pythonw.exe" in cmd and cmd.endswith("main.py\" --overlay")
    cmd2 = startup.startup_command("m.py", str(tmp_path / "other.exe"))
    assert "other.exe" in cmd2
