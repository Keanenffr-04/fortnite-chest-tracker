import json

import numpy as np

from app.capture.recorder import FrameRecorder, default_encoder
from app.capture.screen import ScreenCapture


def fake_frame(v=0):
    return np.full((8, 8, 3), v, dtype=np.uint8)


def enc(frame):
    return bytes([int(frame[0, 0, 0])])


def test_grab_drops_alpha_and_keeps_bgr():
    raw = np.zeros((4, 6, 4), dtype=np.uint8); raw[:, :, 0] = 7
    f = ScreenCapture(grabber=lambda: raw).grab()
    assert f.shape == (4, 6, 3) and f[0, 0, 0] == 7 and f.flags["C_CONTIGUOUS"]


def test_grab_accepts_3_channel():
    f = ScreenCapture(grabber=lambda: np.zeros((2, 2, 3), dtype=np.uint8)).grab()
    assert f.shape == (2, 2, 3)


def test_pre_buffer_is_capped(tmp_path):
    r = FrameRecorder(tmp_path, fps=10, pre_s=1, post_s=1, encoder=enc)
    for i in range(50):
        r.push(fake_frame(i % 200))
    assert len(r._buffer) == 10


def test_mark_saves_pre_plus_post(tmp_path):
    r = FrameRecorder(tmp_path, fps=10, pre_s=1, post_s=0.5, encoder=enc)
    for i in range(20):
        r.push(fake_frame(i))
    assert r.mark("chest")
    out = None
    for i in range(5):
        out = r.push(fake_frame(100 + i)) or out
    assert out is not None and not r.is_saving
    files = sorted(out.glob("frame_*.jpg"))
    assert len(files) == 15                      # 10 before + 5 after
    info = json.loads((out / "info.json").read_text())
    assert info["label"] == "chest" and info["mark_frame_index"] == 9
    assert files[9].read_bytes() == bytes([19])  # the frame at the moment of marking


def test_second_mark_ignored_while_saving(tmp_path):
    r = FrameRecorder(tmp_path, fps=10, pre_s=1, post_s=1, encoder=enc)
    r.push(fake_frame())
    assert r.mark("chest") and not r.mark("negative")


def test_two_saves_same_second_do_not_overwrite(tmp_path):
    r = FrameRecorder(tmp_path, fps=10, pre_s=0.1, post_s=0.1, encoder=enc, wallclock=lambda: 1000.0)
    for _ in range(2):
        r.push(fake_frame()); r.mark("chest"); r.push(fake_frame())
    assert len(r.saved) == 2 and r.saved[0] != r.saved[1]


def test_real_jpeg_encoder_roundtrip(tmp_path):
    try:
        import cv2
    except ImportError:
        return
    data = default_encoder(np.full((64, 64, 3), 120, dtype=np.uint8))
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    assert img.shape == (64, 64, 3) and abs(int(img[0, 0, 0]) - 120) <= 3
