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
