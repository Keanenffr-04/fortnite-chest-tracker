import json

import numpy as np
import pytest

from app.config.settings import Settings
from app.detect.debug import (analyse_folder, format_report, run_detect_debug, run_make_template,
                              sample_folders)
from app.detect.engine import MIN_TEMPLATE_STD, ChestDetector
from app.detect.roi import Roi
from app.detect.templates import Template, load_templates, save_template

cv2 = pytest.importorskip("cv2")


def noise_frame(w=320, h=180, seed=1):
    return np.random.RandomState(seed).randint(0, 256, (h, w, 3), dtype=np.uint8)


def with_patch(frame, patch, x, y):
    out = frame.copy()
    out[y:y + patch.shape[0], x:x + patch.shape[1]] = patch
    return out


def make_patch(seed=7, size=24):
    return np.random.RandomState(seed).randint(0, 256, (size, size, 3), dtype=np.uint8)


def gray_template(patch, name="t", ref_width=None):
    return Template(name, cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY), ref_width)


# ---- ROI -----------------------------------------------------------------
def test_roi_to_pixels_and_clamping():
    assert Roi(0.5, 0.5, 0.25, 0.25).to_pixels(200, 100) == (100, 50, 50, 25)
    x, y, w, h = Roi(0.9, 0.9, 0.9, 0.9).to_pixels(200, 100)      # runs off the edge -> shrunk
    assert x + w <= 200 and y + h <= 100 and w >= 1 and h >= 1
    r = Roi(-1, 5, 0, 0).normalised()
    assert 0 <= r.x <= 0.99 and 0 <= r.y <= 0.99 and r.w >= 0.01 and r.h >= 0.01


def test_roi_crop_shape():
    assert Roi(0.0, 0.0, 0.5, 0.5).crop(np.zeros((100, 200, 3), np.uint8)).shape == (50, 100, 3)


# ---- engine ----------------------------------------------------------------
def test_finds_template_inside_roi_with_full_frame_box():
    patch = make_patch()
    frame = with_patch(noise_frame(), patch, 150, 100)
    det = ChestDetector(Roi(0.4, 0.4, 0.5, 0.5), [gray_template(patch, "open")]).detect(frame)
    assert det.confidence > 0.95 and det.template == "open"
    assert det.box == (150, 100, 24, 24)


def test_unrelated_frame_scores_low():
    det = ChestDetector(Roi(0.0, 0.0, 1.0, 1.0), [gray_template(make_patch())]).detect(noise_frame(seed=99))
    assert det.confidence < 0.5


def test_patch_outside_roi_is_not_found():
    patch = make_patch()
    frame = with_patch(noise_frame(), patch, 10, 10)               # top-left corner
    det = ChestDetector(Roi(0.5, 0.5, 0.5, 0.5), [gray_template(patch)]).detect(frame)
    assert det.confidence < 0.5


def test_best_of_several_templates_wins():
    good, other = make_patch(7), make_patch(8)
    frame = with_patch(noise_frame(), good, 100, 80)
    det = ChestDetector(Roi(0, 0, 1, 1), [gray_template(other, "wrong"), gray_template(good, "right")]).detect(frame)
    assert det.template == "right"


def test_no_templates_or_bad_frame_gives_zero():
    assert ChestDetector(Roi(0, 0, 1, 1), []).detect(noise_frame()).confidence == 0.0
    assert ChestDetector(Roi(0, 0, 1, 1), [gray_template(make_patch())]).detect(np.zeros((0, 0, 3), np.uint8)).template is None


def test_flat_and_oversized_templates_are_skipped_with_reason():
    flat = Template("flat", np.full((10, 10), 128, np.uint8), None)
    big = gray_template(np.zeros((90, 90, 3), np.uint8) + make_patch(size=90)[:, :, :], "big")
    d = ChestDetector(Roi(0.0, 0.0, 0.2, 0.2), [flat, big])           # region is only 64x36 px
    r = d.detect(noise_frame())
    assert r.template is None and set(d.skipped) == {"flat", "big"}
    assert float(flat.gray.std()) < MIN_TEMPLATE_STD


def test_flat_frame_does_not_crash_or_fake_a_match():
    det = ChestDetector(Roi(0, 0, 1, 1), [gray_template(make_patch())]).detect(np.full((180, 320, 3), 50, np.uint8))
    assert 0.0 <= det.confidence < 0.5


def test_template_scales_with_frame_width():
    patch = make_patch(size=24)
    small = cv2.resize(noise_frame(320, 180), (640, 360), interpolation=cv2.INTER_LINEAR)
    big_patch = cv2.resize(patch, (48, 48), interpolation=cv2.INTER_LINEAR)
    frame = with_patch(small, big_patch, 300, 200)                    # game at 640 wide, template cut at 320
    det = ChestDetector(Roi(0, 0, 1, 1), [gray_template(patch, "t", ref_width=320)]).detect(frame)
    assert det.confidence > 0.9 and det.box[2:] == (48, 48)


# ---- templates on disk -----------------------------------------------------
def test_save_and_load_template_roundtrip(tmp_path):
    frame = noise_frame()
    png = save_template(frame, Roi(0.25, 0.25, 0.25, 0.25), "my-chest", tmp_path / "templates")
    assert png.exists()
    (t,) = load_templates(tmp_path / "templates")
    assert t.name == "my-chest" and t.ref_width == 320 and t.gray.ndim == 2


def test_bad_template_names_and_tiny_boxes_refused(tmp_path):
    for bad in ("", "a b", "../x", "x" * 41):
        with pytest.raises(ValueError):
            save_template(noise_frame(), Roi(0.1, 0.1, 0.3, 0.3), bad, tmp_path)
    with pytest.raises(ValueError):
        save_template(noise_frame(), Roi(0.1, 0.1, 0.001, 0.001), "tiny", tmp_path)


def test_load_templates_missing_folder_and_corrupt_file(tmp_path):
    assert load_templates(tmp_path / "nope") == []
    (tmp_path / "broken.png").write_bytes(b"not a png")
    assert load_templates(tmp_path) == []


# ---- debug view -----------------------------------------------------------
def write_sample(root, name, label, patch_at, patch, n=6, mark=3):
    folder = root / name
    folder.mkdir(parents=True)
    for i in range(n):
        f = noise_frame(seed=100 + i)
        if patch_at is not None and i >= mark:
            f = with_patch(f, patch, *patch_at)
        cv2.imwrite(str(folder / f"frame_{i:03d}.jpg"), f, [cv2.IMWRITE_JPEG_QUALITY, 98])
    (folder / "info.json").write_text(json.dumps({"label": label, "mark_frame_index": mark}))
    return folder


def test_analyse_folder_chest_detected_negative_ok(tmp_path):
    patch = make_patch(size=32)
    chest = write_sample(tmp_path, "a_chest", "chest", (140, 90), patch)
    neg = write_sample(tmp_path, "b_negative", "negative", None, patch)
    det = ChestDetector(Roi(0.3, 0.3, 0.6, 0.6), [gray_template(patch, "open")])
    r1 = analyse_folder(chest, det, out_dir=tmp_path / "out")
    r2 = analyse_folder(neg, det)
    assert r1.verdict(0.8) == "DETECTED" and r1.peak_index >= 3 and r1.label == "chest"
    assert r2.verdict(0.8).startswith("ok")
    assert len(list((tmp_path / "out").glob("*.jpg"))) == 6      # annotated pictures written
    assert "DETECTED" in format_report(r1, 0.8) and "you pressed the key" in format_report(r1, 0.8)


def test_verdicts_for_missed_false_alarm_and_unknown(tmp_path):
    patch = make_patch(size=32)
    missed = write_sample(tmp_path, "m", "chest", None, patch)
    false = write_sample(tmp_path, "f", "negative", (140, 90), patch)
    unk = write_sample(tmp_path, "u", "chest", (140, 90), patch)
    (unk / "info.json").unlink()
    det = ChestDetector(Roi(0.3, 0.3, 0.6, 0.6), [gray_template(patch)])
    assert analyse_folder(missed, det).verdict(0.8) == "MISSED"
    assert analyse_folder(false, det).verdict(0.8) == "FALSE ALARM"
    assert analyse_folder(unk, det).verdict(0.8) == "would count"


def test_sample_folders_accepts_one_folder_or_a_parent(tmp_path):
    patch = make_patch()
    a = write_sample(tmp_path, "a", "chest", (140, 90), patch)
    write_sample(tmp_path, "b", "negative", None, patch)
    assert sample_folders(a) == [a]
    assert [p.name for p in sample_folders(tmp_path)] == ["a", "b"]
    assert sample_folders(tmp_path / "missing") == []


def test_cli_make_template_then_debug_end_to_end(tmp_path, capsys):
    s = Settings(); s.data_dir = str(tmp_path / "data")
    s.detection_roi_x, s.detection_roi_y, s.detection_roi_w, s.detection_roi_h = 0.3, 0.3, 0.6, 0.6
    patch = make_patch(size=32)
    sample = write_sample(tmp_path, "s1", "chest", (140, 90), patch)
    ref = tmp_path / "ref.png"
    cv2.imwrite(str(ref), with_patch(noise_frame(seed=5), patch, 140, 90))
    # 32px patch at (140,90) in a 320x180 frame = fractions 0.4375, 0.5, 0.1, 0.1778
    assert run_make_template(ref, "open", 0.4375, 0.5, 0.1, 0.1778, s) == 0
    assert run_detect_debug(sample, s, out_root=tmp_path / "dbg") == 0
    out = capsys.readouterr().out
    assert "1 detected, 0 missed, 0 false alarm" in out and (tmp_path / "dbg" / "s1").is_dir()


def test_debug_without_templates_or_samples_explains(tmp_path, capsys):
    s = Settings(); s.data_dir = str(tmp_path / "data")
    assert run_detect_debug(tmp_path, s) == 1 and "No templates" in capsys.readouterr().out
    assert run_make_template(tmp_path / "nope.png", "x", 0, 0, 1, 1, s) == 1


# ---- settings -------------------------------------------------------------
def test_roi_settings_default_and_clamped(tmp_path):
    s = Settings()
    assert (s.detection_roi_x, s.detection_roi_y, s.detection_roi_w, s.detection_roi_h) == (0.30, 0.55, 0.40, 0.35)
    s.detection_roi_x, s.detection_roi_w = 0.9, 0.9
    s.validate()
    assert s.detection_roi_x + s.detection_roi_w <= 1.0 + 1e-9


def test_old_settings_file_without_roi_still_loads(tmp_path):
    p = tmp_path / "s.json"; p.write_text('{"overlay_scale": 2.0}')
    s = Settings.load(p)
    assert s.overlay_scale == 2.0 and s.detection_roi_w == 0.40
