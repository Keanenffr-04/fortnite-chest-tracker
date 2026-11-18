"""Command-line tools: --record (collect samples) and --benchmark (measure capture cost)."""
from __future__ import annotations

import time

from app.capture.recorder import FrameRecorder, default_encoder
from app.capture.screen import ScreenCapture
from app.config.settings import Settings, app_data_dir


def run_benchmark(seconds: float = 5.0, settings: Settings | None = None) -> int:
    s = settings or Settings.load()
    cap = ScreenCapture(s.capture_monitor)
    grab_t, enc_t, n = 0.0, 0.0, 0
    cpu0, wall0 = time.process_time(), time.perf_counter()
    try:
        while time.perf_counter() - wall0 < seconds:
            t0 = time.perf_counter(); frame = cap.grab(); t1 = time.perf_counter()
            default_encoder(frame); t2 = time.perf_counter()
            grab_t += t1 - t0; enc_t += t2 - t1; n += 1
    finally:
        cap.close()
    wall = time.perf_counter() - wall0
    cpu = time.process_time() - cpu0
    print(f"Frame size: {frame.shape[1]}x{frame.shape[0]}")
    print(f"Frames: {n} in {wall:.1f}s (back-to-back, no throttling)")
    print(f"Avg grab:   {grab_t / n * 1000:.1f} ms")
    print(f"Avg encode: {enc_t / n * 1000:.1f} ms")
    print(f"Max rate:   {n / wall:.1f} fps")
    print(f"CPU used by this process: {cpu / wall * 100:.0f}% of one core while running flat out")
    print("Note: at your 10 fps setting the load will be far lower than this worst case.")
    return 0


def run_record(settings: Settings | None = None) -> int:
    s = settings or Settings.load()
    try:
        import keyboard
    except ImportError:
        print("The 'keyboard' package is missing. Run: python -m pip install -r requirements.txt")
        return 1
    fps = 1000.0 / s.detection_interval_ms
    out = app_data_dir() / "captures"
    out.mkdir(exist_ok=True)
    rec = FrameRecorder(out, fps=fps, pre_s=s.record_pre_s, post_s=s.record_post_s)
    cap = ScreenCapture(s.capture_monitor)
    flags = {"chest": False, "negative": False, "stop": False}
    keyboard.add_hotkey(s.hotkey_mark_chest, lambda: flags.__setitem__("chest", True))
    keyboard.add_hotkey(s.hotkey_mark_negative, lambda: flags.__setitem__("negative", True))
    keyboard.add_hotkey(s.hotkey_stop_recording, lambda: flags.__setitem__("stop", True))
    print(f"Recording at {fps:.0f} fps. Samples go to: {out}")
    print(f"  {s.hotkey_mark_chest.upper()} = a chest JUST opened   |  "
          f"{s.hotkey_mark_negative.upper()} = nothing special (negative sample)  |  "
          f"{s.hotkey_stop_recording.upper()} = stop")
    interval = s.detection_interval_ms / 1000.0
    try:
        while not flags["stop"]:
            t0 = time.perf_counter()
            if flags["chest"]:
                flags["chest"] = False
                print("Saved-in-progress: chest sample" if rec.mark("chest") else "Busy saving, press again in a moment")
            if flags["negative"]:
                flags["negative"] = False
                print("Saved-in-progress: negative sample" if rec.mark("negative") else "Busy saving, press again in a moment")
            folder = rec.push(cap.grab())
            if folder:
                print(f"Saved: {folder}")
            time.sleep(max(0.0, interval - (time.perf_counter() - t0)))
    except KeyboardInterrupt:
        pass
    finally:
        cap.close()
        keyboard.unhook_all()
    print(f"Done. {len(rec.saved)} sample(s) saved in {out}")
    return 0
