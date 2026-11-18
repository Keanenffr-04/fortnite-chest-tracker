"""Sample recorder.

Keeps the last `pre_s` seconds of frames in memory (as compressed JPEG bytes, so 1080p costs
~0.3 MB per frame instead of ~6 MB). When you press the mark key it saves those frames plus the
next `post_s` seconds into a folder. These folders are the real-gameplay samples v1.1.3 needs.
"""
from __future__ import annotations

import json
import time
from collections import deque
from pathlib import Path


def default_encoder(frame) -> bytes:
    import cv2
    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if not ok:
        raise RuntimeError("JPEG encoding failed")
    return buf.tobytes()


class FrameRecorder:
    def __init__(self, out_dir, fps: float = 10.0, pre_s: float = 5.0, post_s: float = 3.0,
                 encoder=default_encoder, wallclock=time.time):
        self.out_dir = Path(out_dir)
        self.fps = fps
        self.pre_frames = max(1, int(pre_s * fps))
        self.post_frames = max(1, int(post_s * fps))
        self._encode = encoder
        self._wall = wallclock
        self._buffer: deque[bytes] = deque(maxlen=self.pre_frames)
        self._pending: dict | None = None
        self.saved: list[Path] = []

    @property
    def is_saving(self) -> bool:
        return self._pending is not None

    def mark(self, label: str) -> bool:
        """Start saving around this moment. Ignored (False) if a save is already in progress."""
        if self._pending is not None:
            return False
        frames = list(self._buffer)
        self._pending = {"label": label, "frames": frames, "mark_index": max(0, len(frames) - 1),
                         "remaining": self.post_frames, "t": self._wall()}
        return True

    def push(self, frame) -> Path | None:
        """Feed one frame. Returns the folder path when a pending save finishes."""
        data = self._encode(frame)
        self._buffer.append(data)
        p = self._pending
        if p is None:
            return None
        p["frames"].append(data)
        p["remaining"] -= 1
        if p["remaining"] <= 0:
            self._pending = None
            return self._write(p)
        return None

    def _write(self, p: dict) -> Path:
        stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(p["t"]))
        folder = self.out_dir / f"{stamp}_{p['label']}"
        n = 1
        while folder.exists():
            n += 1
            folder = self.out_dir / f"{stamp}_{p['label']}_{n}"
        folder.mkdir(parents=True)
        for i, data in enumerate(p["frames"]):
            (folder / f"frame_{i:03d}.jpg").write_bytes(data)
        (folder / "info.json").write_text(json.dumps({
            "label": p["label"], "fps": self.fps, "frames": len(p["frames"]),
            "mark_frame_index": p["mark_index"]}, indent=2), encoding="utf-8")
        self.saved.append(folder)
        return folder
