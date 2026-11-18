# Roadmap

[x] = done and tested on synthetic data | [ ] = not done.
"Written, not run" means the code exists but has never run on a real PC / real Fortnite.
Nothing here has been tested against real Fortnite yet.

Versioning: v1.1.1 -> v1.1.16, then v1.2.1 -> v1.2.x, then v1.3.x. One git branch per version.

# MILESTONE 1 - Working tracker for you (v1.1.x)

## v1.1.1 - Foundation  [done]
- [x] Counter, SQLite, settings, CSV export, tests, CI
- [ ] Licence (waiting on you to choose)

## v1.1.2 - Screen capture + sample recorder  [done]
- [x] Capture, recorder, `--benchmark` (run on your PC: 45.5 ms grab, 17.6 fps max)
- [ ] YOU: record real chest samples (needed for v1.1.10)

## v1.1.3 - Overlay (basic)  [done, written not run]
- [x] Frameless always-on-top overlay, draggable, manual counting
- [ ] YOU: confirm it looks right

## v1.1.4 - Hotkeys, click-through, launcher  [done, written not run]
- [x] Global hotkeys, LOCKED click-through, double-click launcher (`run.bat` until v1.1.11, then `FortniteChestTracker.pyw`)
- [ ] YOU: test hotkeys while Fortnite is focused

## v1.1.5 - Detection sound + overlay customisation  [done, written not run]
- [x] Notification sounds (rising = counted, falling = removed), volume setting - WAV generation unit-tested
- [x] Right-click menu: opacity, size, theme, show/hide status/session/timer, sound on/off
- [x] Option validation, old settings files still load - unit-tested
- [ ] YOU: check the menu works and the sound plays (needs Windows)

## v1.1.6 - Dashboard + Live Tracker page + Settings page  [done, written not run]
- [x] Main window (`--app`), dark theme, purple/blue cards - theme colour follows the overlay theme
- [x] Dashboard: stat cards + recent matches
- [x] Live Tracker: counter, status, recent events, manual correction, show/hide overlay
- [x] Settings page (overlay, hotkeys, detection, sound, startup, data, reset) - validation, hotkey conflicts, start-with-Windows unit-tested with a fake registry
- [ ] YOU: run `run.bat`; check all three pages look right, Apply works, the overlay follows setting changes
- [ ] YOU: tick "Start with Windows", reboot/sign out, check the overlay appears; untick and check it stops
- [ ] YOU: change a hotkey in Settings and check the new one works in Fortnite (and the old one stops)
## v1.1.7 - Stream button  [done, written not run]
- [x] Overlay stays hidden when the app opens; **Start stream** / **Stop stream** button in the sidebar shows / hides it
- [x] Hotkey and overlay-menu hide/show stay in sync with the button - controller logic unit-tested
- [ ] YOU: run `run.bat`; check the overlay is hidden at start, Start stream shows it, Stop stream hides it, Ctrl+Shift+O keeps the button label right
## v1.1.8 - Match history + CSV export  [done, written not run]
- [x] History page: every finished match, newest first
- [x] Export CSV button (save dialog, success/error message) - export logic unit-tested
- [ ] YOU: finish a couple of matches, open History, check they are listed; press Export CSV and open the file in Excel
## v1.1.9 - Dashboard chart + daily/weekly totals  [done, written not run]
- [x] Bar chart of chests per match (last 20)
- [x] Today / Last 7 days cards - date maths unit-tested
- [ ] YOU: finish a few matches, check the chart and both cards look right and update when you press +1
## v1.1.10 - Detection engine v1 + debug view  [done, written not run]
- [x] Region (ROI) template detector with confidence score - unit-tested on synthetic frames only
- [x] Detection debug view: `--make-template`, `--detect-debug` (per-frame confidence, DETECTED / MISSED / FALSE ALARM, annotated pictures)
- [ ] YOU: record real chest samples (`--record`), cut a template from one, run `--detect-debug` and send me the output + a few annotated pictures
- Not wired into the live counter yet
## v1.1.11 - Launcher without .bat  [done, written not run]
- [x] `FortniteChestTracker.pyw` replaces `run.bat`: double-click, no console window, installs missing packages on first start, errors shown in a message box - launcher logic unit-tested
- [ ] YOU: double-click it; check the main window opens with no black window. Test the first-run install if you can (e.g. in a fresh venv)
- Only 1 change this version (the 2nd slot stayed free to keep it small)
## v1.1.12 - Personal-best star + chart per day  [this release, written not run]
- [x] History page: your best match(es) get a gold star and bold gold chest count (ties all count) - logic unit-tested
- [x] Dashboard chart: **Show per day / Show per match** button (last 14 days, today on the right, the match in progress counts as today) - date maths unit-tested
- [ ] YOU: finish a few matches; check the star on History and the per-day toggle on the Dashboard
- Taken from the Backlog because calibration/detection need your real samples (not received yet)
## v1.1.13 - Calibration + switch detection on (NEEDS your real samples)
- [ ] Calibration screen: confirm resolution + set the watch region (basis for friends' setups)
- [ ] Switch detection on in the live counter (status shows Detecting)
## v1.1.14 - Event validation + replay tests (NEEDS your real samples)
- [ ] Event state machine (prompt -> hold -> open) to cut false positives
- [ ] Replay tests from recorded frames, accuracy numbers
## v1.1.15 - Auto match + logging
- [ ] Auto match start/reset (experimental, needs samples)
- [ ] Log file + "open logs" button (so a friend can send you a crash report)
## v1.1.16 - Packaging
- [ ] `.exe` build, release ZIP (replaces the .pyw for friends)
- [ ] Real-gameplay test guide
# MILESTONE 2 - Ready for friends (v1.2.x)

## v1.2.1 - Real-gameplay accuracy tuning
- [ ] Tune thresholds on your real matches; fix duplicates / misses
## v1.2.2 - Resolution + HUD support
- [ ] 1080p, 1440p, 720p; HUD scale; clear "unsupported setup" message
## v1.2.3 - "Report a miss / false count" button
- [ ] One click saves the last few seconds of frames locally (nothing uploads automatically)
- [ ] Friends send you these to improve detection on their setups
## v1.2.4 - Update check
- [ ] Notify when a new GitHub release exists, with a link
## v1.2.5 - First-run guide
- [ ] What to set in Fortnite (Windowed Fullscreen), hotkeys, calibration walkthrough
## v1.2.6 - Profiles + backups
- [ ] Separate stats/settings per friend on a shared PC
- [ ] Automatic daily database backup (keep newest 30), "Back up now" button
## v1.2.7 - Proper installer
- [ ] Single installer (no Python/pip), start-with-Windows option, uninstall

# MILESTONE 3 - Extras (v1.3.x, order flexible)
- [ ] Shareable stats card (image: "47 chests this week")
- [ ] OBS browser-source overlay (the in-game overlay does not show in stream captures)
- [ ] Goals and streaks (e.g. "30 chests this week")
- [ ] Discord status showing the match count
- [ ] Friends leaderboard: start with exporting a file and comparing; a server only if wanted (needs consent + privacy care)
- [ ] Evaluate Windows RegisterHotKey instead of the `keyboard` global hook (lighter footprint)

# Backlog (ideas waiting for a version - rule: max 2 changes per version, the rest lands here)
- Match comparison
- Chart over time: per week view (per day was done in v1.1.12)
(Add new ideas below. Charts and daily/weekly totals were done in v1.1.9; personal-best highlight + per-day chart in v1.1.12.)

# Before sharing with friends (checklist)
- [ ] Choose a licence (I will not pick one without asking)
- [ ] Read Epic's current anti-cheat / third-party-tool policy. We never read memory or inject code, but no overlay or global key hook is guaranteed safe. Tell friends the risk.
- [ ] Privacy: "report a miss" frames are screenshots of their game; keep them local and manual to send
- [ ] Test on at least one other PC with different resolution/GPU

# Known limits
- The detection engine (v1.1.10) exists but is not switched on and has never seen real Fortnite; it needs real samples from you.
- The overlay is manual-count only until it is switched on (v1.1.13).
- Fortnite should run in Windowed Fullscreen for the overlay to show.
