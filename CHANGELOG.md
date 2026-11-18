# Changelog

## v1.1.5
- Added: notification sounds (generated WAVs, played with winsound), volume setting
- Added: right-click menu for opacity, size, theme (violet/blue/green/red), show/hide status/session/timer, sound
- Added: 11 tests (42 total). Qt menu and audio untested until run on Windows
- Roadmap: rewritten with friends-release milestones (v1.2.x) and extras (v1.3.x)

## v1.1.4
- Added: global hotkeys, click-through (LOCKED) mode, hotkey validation, smarter run.bat
- Fixed: stale "overlay not built" message
- Added: 5 tests (31 total). Hotkeys and click-through untested until run on Windows
- Roadmap: sound + customisation moved to v1.1.5, everything after shifted by one

## v1.1.3
- Added: floating overlay (PySide6) with manual counting, `--overlay`, PySide6 requirement
- Added: 4 tests (26 total). The Qt window itself is untested until run on Windows
- Roadmap reordered: detector moved to v1.1.7 so overlay/dashboard can be built while samples are collected
- Still not included: detection, hotkeys, dashboard

## v1.1.2
- Added: screen capture (mss), sample recorder, `--record`, `--benchmark`, capture settings
- Added: 7 tests (22 total). Real screen capture and hotkeys are untested until run on Windows
- Still not included: detection, overlay, dashboard

## v1.1.1
- Added: counter, SQLite database, settings, CSV export, tests, CI
- Not included: detection, overlay, dashboard
