# Roadmap

[x] = done and tested on synthetic data | [ ] = not done.
Nothing here has been tested against real Fortnite yet.

## v1.1.1 - Foundation
- [x] Counter (cooldown, confidence, manual +/-, match reset)
- [x] SQLite storage, stats, CSV export
- [x] Settings file
- [x] Unit tests + GitHub Actions
- [ ] Licence (waiting on you to choose)

## v1.1.2 - Screen capture + frame recorder (so you can give me real samples)
- [x] Screen capture module (mss) - code written; NOT yet tested on a real screen
- [x] Sample recorder with ring buffer + hotkeys (F8 chest / F9 negative / F10 stop) - logic unit-tested, hotkeys NOT yet tested on Windows
- [x] Capture benchmark (`--benchmark`) - NOT yet run on your PC
- [x] Benchmark run on your PC: 45.5 ms grab, 11.2 ms encode, 17.6 fps max (desktop, not in-game)
- [ ] YOU: record real chest samples (needed before the detector version, see README)
## v1.1.3 - Overlay (basic)
- [x] Display logic (timer, size, on-screen clamp) - unit-tested
- [x] Overlay window: frameless, always-on-top, rounded, purple/blue, draggable, right-click menu - code written, NOT yet run (needs PySide6 on your PC)
- [x] `--overlay` runs it with manual counting, saves matches to the database
- [ ] YOU: confirm the overlay looks right on your PC (first real run of the Qt code)
## v1.1.4 - Hotkeys, click-through, double-click launcher
- [x] Hotkey rules: validation, duplicate + unsafe-key detection - unit-tested
- [x] Global hotkeys (toggle overlay, +1, -1, click-through, quit) via `keyboard` - code written, NOT yet tested on Windows
- [x] Click-through "LOCKED" mode - code written, NOT yet tested on Windows
- [x] `run.bat` installs missing packages and opens the overlay
- [x] Safety: hide/lock only offered when a hotkey can undo them
- [ ] YOU: test hotkeys (including while Fortnite is focused) and click-through
## v1.1.5 - Detection sound + overlay customisation (opacity, size, layout)
## v1.1.6 - Dashboard + Live Tracker page + Settings page
## v1.1.7 - Statistics, charts, match history, CSV export button
## v1.1.8 - Detection engine v1 + debug view (NEEDS your real samples)
## v1.1.9 - Event validation, replay tests, auto match detection (experimental)
## v1.1.10 - Packaging (.exe), release ZIP, real-gameplay test guide
## v1.2.1+ - Accuracy tuning on real gameplay, bug fixes, optimisation

## Known limits
- No chest detection exists until v1.1.8, and it needs real Fortnite samples from you.
- The overlay is manual-count only until then.
- Fortnite should run in Windowed Fullscreen for the overlay to show.
- Hotkeys use the `keyboard` package (a global key hook). To evaluate later: Windows RegisterHotKey, which is lighter and avoids a global hook.
- Default hotkeys can be changed by editing settings.json (settings UI arrives v1.1.6).
