# Changelog

## v1.1.7
- Changed: the overlay no longer appears when the main window opens. Press **Start stream** (sidebar, visible on every page) to show it; the button becomes **Stop stream** to hide it. The Ctrl+Shift+O hotkey and the overlay's right-click "Hide overlay" do the same thing and keep the button in step
- Changed: "Start stream" is per run and not saved, so the main window always opens with the overlay hidden. `--overlay` (and start with Windows) still shows the overlay immediately
- Removed: the "Hide/Show overlay" button on the Live Tracker page and the "Show overlay" tick on the Settings page (the Stream button replaces both). Old settings files that still contain it load fine
- Tests: 80 total (2 new). The Qt button itself is untested until run on Windows
- Roadmap: planned versions shifted by one (charts v1.1.8, detection v1.1.9); a Backlog section was added

## v1.1.6
- Added: main window (`--app`, now what `run.bat` opens) with a dark purple/blue theme and three pages
- Added: Dashboard (this match / session / total / matches / average / personal best + recent matches)
- Added: Live Tracker (big counter, status, match time, +1 / -1 / New match, recent events list, show/hide overlay)
- Added: Settings page (overlay, hotkeys, detection, sound + test sound, start with Windows, open data folder, reset statistics, reset settings). Hotkeys can now be changed in the app; invalid or duplicate hotkeys are refused with a reason and nothing is half-saved
- Added: start with Windows (per-user registry Run entry, starts the overlay only)
- Changed: overlay and window share one `TrackerController` (counts, settings, sound, database), so they always agree. Hotkeys are only re-registered when one actually changed
- Added: 36 tests (78 total) for the controller, settings validation, stats/formatting, theme and startup. The Qt windows and the Windows registry call are untested until run on Windows
- Not included yet: charts, full match history, CSV export button (v1.1.7); detection (v1.1.8)

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
