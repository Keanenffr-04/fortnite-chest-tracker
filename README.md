# Fortnite Live Chest Tracker - v1.1.1

Counts chests you open in Fortnite and shows a live overlay. Local Windows app, works offline.

## Status
The tracker is NOT functional yet. v1.1.1 is the foundation only (counter + database + settings).
Detection, overlay and dashboard are not built. See ROADMAP.md.

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
