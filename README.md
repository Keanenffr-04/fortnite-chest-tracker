# Fortnite Live Chest Tracker - v1.1.3

Counts chests you open in Fortnite and shows a live overlay. Local Windows app, works offline.

## Status
The tracker is NOT functional yet. v1.1.3 adds a basic overlay (manual counting). v1.1.2 added screen capture and a sample recorder.
Detection, overlay and dashboard are not built. See ROADMAP.md.

## Install
```powershell
python -m pip install -r requirements.txt
```

## Try the overlay
`python main.py --overlay` - drag it with the left mouse button, right-click for Add chest / Remove chest / New match / Quit.
It counts manually for now. Automatic detection comes later.

## Collect real chest samples (this is what v1.1.3 needs)
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
