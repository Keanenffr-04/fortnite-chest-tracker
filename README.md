# Fortnite Live Chest Tracker - v1.1.14

Counts chests you open in Fortnite and shows a live overlay. Local Windows app, works offline.

## Status
Automatic chest detection is NOT built yet: you count manually (hotkeys, overlay menu or the Live Tracker page).
v1.1.7: the overlay (the small box) no longer pops up on its own. Press **Start stream** in the main window's
sidebar to show it, **Stop stream** to hide it. v1.1.8 added a History page with an Export CSV button; v1.1.9 added a chests-per-match chart and Today / Last 7 days
cards to the Dashboard. v1.1.10 adds the detection engine and a debug tool (command line only, not wired into the live counter yet). v1.1.11 replaces `run.bat` with a double-click `FortniteChestTracker.pyw`. v1.1.12: your personal-best matches get a gold star on the History page, and the Dashboard chart can switch between per match and per day. v1.1.13: the History page has a **chests opened on this day** card (arrows to pick a day), and the Dashboard/History tables are tidier. v1.1.14: Live Tracker and Settings are tidied (cards, hover tips, plain-English text). The pirate-token look is planned for v1.1.15.
Nothing has been tested on real Fortnite yet. See ROADMAP.md.

## Install
```powershell
python -m pip install -r requirements.txt
```

## Try the app
Double-click `FortniteChestTracker.pyw` (no black console window; installs missing packages the first time, then opens the main window; errors show in a message box). The overlay stays
hidden until you press **Start stream**.
Closing the main window quits the tracker. `python main.py --overlay` starts just the overlay (it shows straight away, as there is no window to press a button in).

Overlay: drag with the left mouse button; right-click for the menu: add/remove chest, new match, opacity,
size, theme, what to show, sound on/off. It counts manually for now (a rising chime = counted).

| Hotkey | Action |
|---|---|
| Ctrl+Shift+O | Hide / show overlay |
| Ctrl+Shift+Up / Down | Add / remove a chest |
| Ctrl+Shift+C | Click-through (LOCKED) on/off |
| Ctrl+Shift+Q | Quit |

Change them on the Settings page (empty = disabled; they need ctrl/alt/shift so they don't fire while you play).

## Collect real chest samples (the detector needs these)
1. Set Fortnite to Windowed Fullscreen, 1920x1080.
2. `python main.py --benchmark` and send me the output (checks capture speed).
3. `python main.py --record`, then start a match.
4. When a chest JUST opened, press **F8**. Do this for ~20 chests (different chest types if you can).
5. Press **F9** at ~20 normal moments (running, looting, menus, near an unopened chest) as negative samples.
6. **F10** stops. Samples are saved in `%APPDATA%\FortniteChestTracker\captures\`.
7. Zip a few of those folders and send them to me. They contain only screenshots of your game.

## Detection engine (v1.1.10 - for testing on your samples)
It looks for small reference pictures (**templates**) inside a watch region of the screen and gives a confidence
0.0-1.0. It only knows what you show it, so it needs templates cut from YOUR recorded samples.
1. Open a chest sample frame, e.g. `captures\<folder>\frame_030.jpg`, and note the box around what appears when
   a chest opens, as fractions of the screen (x, y = top-left, w, h = size; 0-1).
2. `python main.py --make-template frame_030.jpg open_chest 0.42 0.60 0.15 0.10`
3. `python main.py --detect-debug "%APPDATA%\FortniteChestTracker\captures"` runs every sample folder, prints the
   confidence per frame and DETECTED / MISSED / FALSE ALARM per sample, and saves annotated pictures to
   `%APPDATA%\FortniteChestTracker\debug\` (green = watch region, yellow = best match).
The watch region is `detection_roi_x/y/w/h` in `settings.json` (default is a placeholder guess; the calibration
screen in v1.1.11 will set it for you). The live counter does not use the detector yet.

## Run
Install Python 3.10+ (tick "Add Python to PATH"), then double-click `FortniteChestTracker.pyw`.
If double-click does nothing, right-click it > Open with > Python (pythonw). The command-line tools (`--record`, `--detect-debug`, ...) are still run as `python main.py ...`.
Self-test: `python main.py --selftest`   Tests: `python -m pytest -q`

## Put it on GitHub (when you're ready)
```powershell
git init
git add .
git commit -m "chore: initial commit v1.1.1"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```
Create the empty repo on github.com first. Branches: `git checkout -b feature/name`.
Commit style: `feat:`, `fix:`, `docs:`, `test:`.

## Safety
Screen pixels only. No memory reading, no injection, no game modification.
