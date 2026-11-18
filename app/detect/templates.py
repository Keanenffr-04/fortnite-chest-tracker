"""Reference templates: small crops of the game screen that mean "a chest was just opened".

You create them from your own recorded sample frames (`--make-template`). Each template is a PNG
plus a small JSON file remembering the frame width it was cut from, so it can be scaled when
the game runs at a different resolution (basic scaling only - proper resolution support is v1.2.2).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.detect.roi import Roi

_NAME_OK = re.compile(r"^[A-Za-z0-9_-]{1,40}$")


@dataclass(frozen=True)
class Template:
    name: str
    gray: np.ndarray        # 2-D uint8
    ref_width: int | None   # frame width the crop was cut from (None = do not scale)


def templates_dir(data_dir) -> Path:
    return Path(data_dir) / "templates"


def to_gray(img: np.ndarray) -> np.ndarray:
    import cv2
    if img.ndim == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def save_template(frame: np.ndarray, box: Roi, name: str, folder) -> Path:
    """Cut `box` out of `frame` and store it as <folder>/<name>.png (+ .json). Returns the PNG path."""
    import cv2
    if not _NAME_OK.match(name):
        raise ValueError("Template name: 1-40 letters, digits, - or _ only")
    crop = box.crop(frame)
    if crop.shape[0] < 4 or crop.shape[1] < 4:
        raise ValueError("That box is too small (under 4x4 pixels)")
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    png = folder / f"{name}.png"
    if not cv2.imwrite(str(png), crop):
        raise OSError(f"Could not write {png}")
    (folder / f"{name}.json").write_text(json.dumps({"ref_width": int(frame.shape[1])}), encoding="utf-8")
    return png


def load_templates(folder) -> list[Template]:
    """Every readable template in the folder, sorted by name. Unreadable files are skipped."""
    import cv2
    folder = Path(folder)
    out: list[Template] = []
    if not folder.is_dir():
        return out
    for png in sorted(folder.glob("*.png")):
        img = cv2.imread(str(png), cv2.IMREAD_COLOR)
        if img is None:
            continue
        ref = None
        meta = png.with_suffix(".json")
        try:
            ref = int(json.loads(meta.read_text(encoding="utf-8"))["ref_width"])
        except (OSError, ValueError, KeyError, TypeError):
            pass
        out.append(Template(png.stem, to_gray(img), ref))
    return out
