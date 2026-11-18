"""Detection engine v1: template matching inside a watch region (ROI).

For every frame: crop the ROI, turn it to grey, slide each reference template over it and take the
best normalised correlation (0.0-1.0) as the confidence. ChestCounter then applies sensitivity and
cooldown, exactly as it does for manual counts.

IMPORTANT: this only answers "does this frame look like one of my templates?". Until the templates
are cut from real Fortnite samples, the confidence numbers mean nothing for real gameplay.
Event validation (prompt -> hold -> open) comes in v1.1.11.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.detect.roi import Roi
from app.detect.templates import Template, to_gray

MIN_TEMPLATE_STD = 2.0   # a (nearly) flat template matches everything equally - refuse it


@dataclass(frozen=True)
class Detection:
    confidence: float                       # 0.0 - 1.0
    template: str | None                    # best template's name, None if nothing could be compared
    box: tuple[int, int, int, int] | None   # (x, y, w, h) of the best match in FULL-frame pixels


NO_DETECTION = Detection(0.0, None, None)


class ChestDetector:
    def __init__(self, roi: Roi, templates: list[Template]):
        self.roi = roi.normalised()
        self.templates = list(templates)
        self.skipped: dict[str, str] = {}   # template name -> why it was not used (last detect call)

    def set_roi(self, roi: Roi) -> None:
        self.roi = roi.normalised()

    def detect(self, frame: np.ndarray) -> Detection:
        import cv2
        self.skipped = {}
        if frame is None or frame.ndim < 2 or frame.size == 0 or not self.templates:
            return NO_DETECTION
        fh, fw = frame.shape[:2]
        rx, ry, rw, rh = self.roi.to_pixels(fw, fh)
        region = to_gray(frame[ry:ry + rh, rx:rx + rw])
        best = NO_DETECTION
        for t in self.templates:
            gray = t.gray
            if t.ref_width and abs(fw / t.ref_width - 1.0) > 0.01:
                s = fw / t.ref_width
                size = (max(1, int(round(gray.shape[1] * s))), max(1, int(round(gray.shape[0] * s))))
                gray = cv2.resize(gray, size, interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)
            th, tw = gray.shape[:2]
            if th > region.shape[0] or tw > region.shape[1]:
                self.skipped[t.name] = "bigger than the watch region"
                continue
            if float(gray.std()) < MIN_TEMPLATE_STD:
                self.skipped[t.name] = "almost one flat colour"
                continue
            res = cv2.matchTemplate(region, gray, cv2.TM_CCOEFF_NORMED)
            res = np.nan_to_num(res, nan=0.0, posinf=0.0, neginf=0.0)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            conf = float(min(1.0, max(0.0, max_val)))
            if conf > best.confidence or best.template is None:
                best = Detection(conf, t.name, (rx + max_loc[0], ry + max_loc[1], tw, th))
        return best
