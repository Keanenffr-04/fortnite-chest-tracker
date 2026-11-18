"""Watch region (ROI) as fractions of the frame, so it does not depend on screen resolution."""
from __future__ import annotations

from dataclasses import dataclass


def _clamp(v: float, lo: float, hi: float) -> float:
    return min(hi, max(lo, float(v)))


@dataclass(frozen=True)
class Roi:
    """x, y = top-left corner; w, h = size. All 0.0-1.0 of the full frame."""
    x: float
    y: float
    w: float
    h: float

    def normalised(self) -> "Roi":
        """Clamp so the box is inside the frame and not smaller than 1% in either direction."""
        x = _clamp(self.x, 0.0, 0.99)
        y = _clamp(self.y, 0.0, 0.99)
        w = _clamp(self.w, 0.01, 1.0 - x)
        h = _clamp(self.h, 0.01, 1.0 - y)
        return Roi(x, y, w, h)

    def to_pixels(self, width: int, height: int) -> tuple[int, int, int, int]:
        """(x, y, w, h) in pixels, always at least 1x1 and inside the frame."""
        r = self.normalised()
        px = min(width - 1, int(round(r.x * width)))
        py = min(height - 1, int(round(r.y * height)))
        pw = max(1, min(width - px, int(round(r.w * width))))
        ph = max(1, min(height - py, int(round(r.h * height))))
        return px, py, pw, ph

    def crop(self, frame):
        h, w = frame.shape[:2]
        x, y, rw, rh = self.to_pixels(w, h)
        return frame[y:y + rh, x:x + rw]
