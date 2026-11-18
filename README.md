# Fortnite Live Chest Tracker - v1.1.6

Counts chests you open in Fortnite and shows a live overlay. Local Windows app, works offline.

## Status
Automatic chest detection is NOT built yet: you count manually (hotkeys, overlay menu or the Live Tracker page).
v1.1.6 adds the main window with Dashboard, Live Tracker and Settings pages. Charts and full history come in v1.1.7,
detection in v1.1.8. Nothing has been tested on real Fortnite yet. See ROADMAP.md.

## Install
```powershell
python -m pip install -r requirements.txt
```

## Try the app
Double-click `run.bat` (installs missing packages the first time, then opens the main window + overlay).
Closing the main window quits the tracker. `python main.py --overlay` starts just the overlay.

Overlay: drag with the left mouse button; right-click for the menu: add/remove chest, new match, opacity,
size, theme, what to show, sound on/off. It counts manually for now (a rising chime = counted).

| Hotkey | Action |
|---|---|
| Ctrl+Shift+O | Hide / show overlay |
| Ctrl+Shift+Up / Down | Add / remove a chest |
| Ctrl+Shift+C | Click-through (LOCKED) on/off |
| Ctrl+Shift+Q | Quit |

Change them on the Settings page (empty = disabled; they need ctrl/alt/shift so they don't fire while you play).

## Collect real chest samples (this is what v1.1.8 needs)
1. Set Fortnite to Windowed Fullscreen, 1920x1080.
2. `python main.py --benchmark` and send me the output (checks capture speed).
3. `python main.py --record`, then start a match.
4. When a chest JUST opened, press **F8**. Do this for ~20 chests (different chest types if you can).
5. Press **F9** at ~20 normal moments (running, looting, menus, near an unopened chest) as negative samples.
6. **F10** stops. Samples are saved in `%APPDATA%\FortniteChestTracker\captures\`.
7. Zip a few of those folders and send them to me. They contain only screenshots of your game.

## Run
Install Python 3.10+ (tick "Add Python to PATH"), then double-click `run.bat`.
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
