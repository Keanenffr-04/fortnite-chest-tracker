"""Detection debug view (`--detect-debug <folder>`): run the detector over recorded samples.

Prints the confidence per frame, says whether each sample would have been counted / missed / a
false alarm at your sensitivity, and saves annotated pictures (ROI box in green, best match box in
yellow, confidence in the corner) so you can SEE what the detector is looking at.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from app.detect.engine import ChestDetector, Detection
from app.detect.roi import Roi


@dataclass
class SampleReport:
    folder: Path
    label: str                      # "chest" | "negative" | "unknown"
    mark_index: int | None
    detections: list[Detection] = field(default_factory=list)
    frame_names: list[str] = field(default_factory=list)

    @property
    def peak_index(self) -> int | None:
        if not self.detections:
            return None
        return max(range(len(self.detections)), key=lambda i: self.detections[i].confidence)

    @property
    def peak(self) -> float:
        i = self.peak_index
        return self.detections[i].confidence if i is not None else 0.0

    def verdict(self, sensitivity: float) -> str:
        hit = self.peak >= sensitivity
        if self.label == "chest":
            return "DETECTED" if hit else "MISSED"
        if self.label == "negative":
            return "FALSE ALARM" if hit else "ok (nothing counted)"
        return "would count" if hit else "would not count"


def frame_files(folder) -> list[Path]:
    return sorted(Path(folder).glob("frame_*.jpg"))


def sample_folders(path) -> list[Path]:
    """`path` is one sample folder, or a folder of sample folders (e.g. the whole captures folder)."""
    path = Path(path)
    if frame_files(path):
        return [path]
    if not path.is_dir():
        return []
    return sorted(p for p in path.iterdir() if p.is_dir() and frame_files(p))


def _read_info(folder: Path) -> tuple[str, int | None]:
    try:
        info = json.loads((folder / "info.json").read_text(encoding="utf-8"))
        return str(info.get("label", "unknown")), info.get("mark_frame_index")
    except (OSError, ValueError):
        return "unknown", None


def analyse_folder(folder, detector: ChestDetector, out_dir=None) -> SampleReport:
    """Run the detector on every frame of one sample folder. Saves annotated frames if out_dir is given."""
    import cv2
    folder = Path(folder)
    label, mark = _read_info(folder)
    rep = SampleReport(folder, label, mark)
    for f in frame_files(folder):
        img = cv2.imread(str(f), cv2.IMREAD_COLOR)
        if img is None:
            continue
        det = detector.detect(img)
        rep.detections.append(det)
        rep.frame_names.append(f.name)
        if out_dir is not None:
            annotate(img, detector.roi, det, Path(out_dir) / f.name)
    return rep


def annotate(frame, roi: Roi, det: Detection, out_path) -> None:
    import cv2
    img = frame.copy()
    h, w = img.shape[:2]
    x, y, rw, rh = roi.to_pixels(w, h)
    cv2.rectangle(img, (x, y), (x + rw, y + rh), (0, 255, 0), 2)
    if det.box:
        bx, by, bw, bh = det.box
        cv2.rectangle(img, (bx, by), (bx + bw, by + bh), (0, 255, 255), 2)
    text = f"{det.confidence:.2f} {det.template or '-'}"
    cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 4)
    cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), img)


def format_report(rep: SampleReport, sensitivity: float) -> str:
    lines = [f"{rep.folder.name}  [{rep.label}]  peak {rep.peak:.2f}"
             f" at frame {rep.peak_index if rep.peak_index is not None else '-'}"
             f"  (marked frame: {rep.mark_index if rep.mark_index is not None else '-'})"
             f"  -> {rep.verdict(sensitivity)}"]
    for i, d in enumerate(rep.detections):
        flag = ""
        if i == rep.mark_index:
            flag += "  <- you pressed the key here"
        if d.confidence >= sensitivity:
            flag += "  *"
        lines.append(f"  {i:3d}  {d.confidence:.2f}  {d.template or '-'}{flag}")
    return "\n".join(lines)


def run_detect_debug(path, settings=None, templates_folder=None, out_root=None) -> int:
    from app.config.settings import Settings
    from app.detect.templates import load_templates, templates_dir
    s = settings or Settings.load()
    tdir = Path(templates_folder) if templates_folder else templates_dir(s.data_dir)
    templates = load_templates(tdir)
    if not templates:
        print(f"No templates found in {tdir}.\n"
              "Make one from a sample frame first, e.g.:\n"
              "  python main.py --make-template <frame.jpg> <name> <x> <y> <w> <h>\n"
              "(x y w h are fractions of the screen, 0-1. See README.)")
        return 1
    folders = sample_folders(path)
    if not folders:
        print(f"No sample folders (with frame_*.jpg) found in {path}")
        return 1
    roi = Roi(s.detection_roi_x, s.detection_roi_y, s.detection_roi_w, s.detection_roi_h)
    det = ChestDetector(roi, templates)
    out_root = Path(out_root) if out_root else Path(s.data_dir) / "debug"
    print(f"Templates: {', '.join(t.name for t in templates)}   Sensitivity: {s.detection_sensitivity:.2f}")
    counts = {"DETECTED": 0, "MISSED": 0, "FALSE ALARM": 0}
    for folder in folders:
        rep = analyse_folder(folder, det, out_dir=out_root / folder.name)
        print(format_report(rep, s.detection_sensitivity))
        v = rep.verdict(s.detection_sensitivity)
        if v in counts:
            counts[v] += 1
    for name, why in det.skipped.items():
        print(f"Note: template '{name}' was not used: {why}")
    print(f"\nSummary: {counts['DETECTED']} detected, {counts['MISSED']} missed, "
          f"{counts['FALSE ALARM']} false alarm(s) across {len(folders)} sample(s).")
    print(f"Annotated pictures: {out_root}")
    return 0


def run_make_template(frame_path, name, x, y, w, h, settings=None) -> int:
    import cv2
    from app.config.settings import Settings
    from app.detect.templates import save_template, templates_dir
    s = settings or Settings.load()
    frame = cv2.imread(str(frame_path), cv2.IMREAD_COLOR)
    if frame is None:
        print(f"Could not read the picture: {frame_path}")
        return 1
    try:
        png = save_template(frame, Roi(x, y, w, h), name, templates_dir(s.data_dir))
    except (ValueError, OSError) as e:
        print(f"Template not saved: {e}")
        return 1
    print(f"Saved template: {png}")
    return 0
