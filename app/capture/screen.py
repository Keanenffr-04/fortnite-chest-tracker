"""Screen capture via mss (reads screen pixels only - never touches the Fortnite process)."""
from __future__ import annotations

import numpy as np


class ScreenCapture:
    """grab() returns one BGR frame (H, W, 3, uint8).

    `grabber` can be injected for tests: a callable returning a BGRA or BGR array.
    `region` is (left, top, width, height) in pixels, or None for the whole monitor.
    """

    def __init__(self, monitor: int = 1, region: tuple[int, int, int, int] | None = None, grabber=None):
        self.monitor = monitor
        self.region = region
        self._grabber = grabber
        self._sct = None

    def _default_grab(self) -> np.ndarray:
        if self._sct is None:
            try:
                import mss
            except ImportError as e:  # pragma: no cover
                raise RuntimeError("mss is not installed. Run: python -m pip install -r requirements.txt") from e
            self._sct = mss.mss()  # must be created and used in the same thread
        if self.region:
            l, t, w, h = self.region
            box = {"left": l, "top": t, "width": w, "height": h}
        else:
            box = self._sct.monitors[self.monitor]
        return np.array(self._sct.grab(box))

    def grab(self) -> np.ndarray:
        raw = self._grabber() if self._grabber else self._default_grab()
        return np.ascontiguousarray(raw[:, :, :3])  # drop alpha channel if present

    def close(self) -> None:
        if self._sct is not None:
            self._sct.close()
            self._sct = None
