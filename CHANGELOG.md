# Changelog

## v1.1.16
- Added: **pirate token** drawn in code: a gold coin with a skull and crossbones (the Pirate Shop token look). Plain shapes and gradients, no copied game art. The coin geometry lives in `app/overlay/pirate.py` (no Qt, tested); `app/overlay/token_icon.py` paints it
- Changed: the overlay in the **Pirate** theme now has its own background: dark chest-brown to black, gold border with a thin inner line, a big faded token behind the number and a small token next to "CHESTS OPENED". The other themes look exactly as before. Pick it in Settings > Theme or right-click the overlay > Theme > Pirate
- Added: `coin_layout()`, `overlay_look()`; 3 new tests (the Qt painting is untested until run on Windows, so check how it looks and tell me what to change)
- Only 2 changes. Your pirate-background request is split over 3 versions: overlay (v1.1.16, this), main window background + token window icon (v1.1.17), overlay polish + per-week chart (v1.1.18). Calibration/detection etc. shift by 1 (see ROADMAP)
- Backlog now: match comparison, per-day table, calendar highlights, tooltips on every button, first-run tips, what to do with the old themes (you said you do not like them: remove them or make Pirate the default, I will ask first), pirate overlay extras

## v1.1.15
- Added: **calendar button** (📅) on the History day card, next to the arrows. Opens a small calendar; click a day and the card jumps to it. Future days cannot be picked. The arrows and **Today** keep working from the picked day
- Added: **Pirate** theme (gold + copper, from the gold coin with a skull and crossbones the Pirate Shop token shows) in Settings > Theme. It colours the overlay, the chart and this window like the other themes
- Added: `days_back_for()`; 2 new tests (the Qt calendar pop-up is untested until run on Windows)
- Only 2 changes. The pirate look is split over 3 versions: colours now (v1.1.15), token icon + overlay restyle (v1.1.16), overlay polish (v1.1.17). Calibration/detection shift by 2 (see ROADMAP)
- Backlog now: match comparison, per-week chart, per-day table, tooltips on every button, friend-friendly first-run tips, calendar highlights days that have matches

## v1.1.14
- Changed (UI tidy, part 2): **Live Tracker** has the status, timer and big counter in one card, taller buttons, hover tips on +1 / -1 / New match, and a friendly "Nothing yet" line instead of an empty list
- Changed: **Settings** sections are now cards, each with a one-line explanation, hover tips on every setting, "Changes take effect when you press Apply", shorter button names, tidier Data card
- Changed: sidebar polish: muted inactive items, clear highlight on the current page, hover tips for each page, taller Start/Stop stream button, styled tooltips everywhere
- Added: `SECTION_BLURBS` + `tooltip()` in the settings model; 1 new test (the Qt pages are untested until run on Windows)
- NOT done: overlay window polish moved into v1.1.15 (the pirate-token look restyles the overlay anyway, so doing it twice would waste work)
- Backlog unchanged

## v1.1.13
- Added: **chests opened on a day** card at the top of the History page. Shows the chests and matches for the chosen day; arrows step back/forward one day, **Today** jumps back. It follows midnight by itself, and the match in progress counts as today (same rule as the Dashboard)
- Changed (UI tidy, part 1 of 2): Dashboard + History tables have alternating rows, no grid lines and roomier rows; the Dashboard lists the last 5 matches (all of them are on History); smaller stat-card numbers so the page fits; the banner now says how to count manually. Spacing tightened
- Added: `Database.totals_between()`, `day_bounds`, `day_totals`, `day_title`, `day_summary`; 5 new tests (the Qt pages are untested until run on Windows)
- Only 2 changes. This was split from your 3-item request into 3 versions: v1.1.13 (this), v1.1.14 (UI tidy part 2: Live Tracker + Settings + overlay polish), v1.1.15 (pirate-token theme). Calibration/detection etc. moved by 3 (see ROADMAP)
- Backlog now: match comparison, per-week chart, per-day table / calendar view, tooltips on every button, friend-friendly first-run tips

## v1.1.12
- Added: personal-best highlight on the History page. Every match equal to your best gets a gold star and a bold gold chest count (ties all get it; a best of 0 is not highlighted). A footnote explains the star
- Added: Dashboard chart toggle **Show per day / Show per match**. Per day = chests per local day for the last 14 days, today on the right; the match in progress counts as today. The caption changes with the view
- Added: `Database.matches_since()`, `daily_values`, `best_flags`, `chests_label`; 2 new tests, 118 total (the Qt pages are untested until run on Windows)
- Both taken from the Backlog (calibration + detection need your real samples, which have not arrived). Moved: calibration + switching detection on to v1.1.13; event validation + replay tests v1.1.14; auto match + logging v1.1.15; packaging v1.1.16
- Backlog now: match comparison, per-week chart

## v1.1.11
- Changed: `run.bat` is gone. Double-click `FortniteChestTracker.pyw` instead: no black console window, installs missing packages the first time (a message tells you to wait), opens the main window. Errors and crashes show in a message box instead of a window that closes. Passing options still works (`pythonw FortniteChestTracker.pyw --overlay`); the start-with-Windows entry is unchanged
- Added: `app/core/launcher.py` (the logic, so it is testable) and 6 tests (116 total, new ones on fakes only). The real double-click, the pip install and the message boxes are untested until run on Windows
- Only 1 change this version (the 2nd slot was left free). Moved: calibration + switching detection on to v1.1.12; event validation + replay tests v1.1.13; auto match + logging v1.1.14; packaging v1.1.15
- Backlog unchanged

## v1.1.10
- Added: detection engine v1 (`app/detect`): template matching inside a watch region (ROI, stored as screen fractions so it does not depend on resolution). Gives a confidence 0-1 per frame and the position of the best match. Templates are scaled if the frame width differs from the one they were cut from (basic only; proper resolution support is v1.2.2). Flat or too-big templates are skipped with a reason
- Added: detection debug view, command line: `--make-template` cuts a template out of a sample frame, `--detect-debug <folder>` runs the detector over recorded samples, prints confidence per frame, says DETECTED / MISSED / FALSE ALARM per sample and saves annotated pictures
- Added: settings `detection_roi_x/y/w/h` (placeholder default; old settings files load fine)
- NOT done: the detector is not connected to the live counter, overlay or status, so counting is still manual. It has never seen real Fortnite: the default region and any confidence numbers are untested until you record samples and run `--detect-debug`
- Moved: the calibration screen to v1.1.11 (kept to 2 changes). Later versions shift by one (packaging + logging is now v1.1.13)
- Tests: 110 total (20 new, all on synthetic frames). Dashboard banner and Detection hint text reworded

## v1.1.9
- Added: bar chart on the Dashboard showing chests per match (last 20, newest on the right, the match in progress is the last bar). It follows the overlay theme colours
- Added: **Today** and **Last 7 days** cards on the Dashboard (today + the 6 days before, by your local midnight). The match in progress counts as today. Cards are now 4 per row
- Taken from the Backlog; detection was NOT started because it needs your recorded samples, so it moves to v1.1.10 (later versions shift by one)
- Tests: 90 total (5 new, 2 updated). The chart drawing is untested until run on Windows

## v1.1.8
- Added: **History** page (sidebar, between Live Tracker and Settings) listing every finished match, newest first, with a one-line total
- Added: **Export CSV** button on the History page. Pick where to save (suggested name `chest_matches_<date>.csv`); you get a message with the number of matches saved, or the reason if it failed. The match in progress is not exported until you press New match
- Parked in the Backlog (kept to 2 changes): charts, daily/weekly totals, match comparison
- Tests: 85 total (5 new). The Qt page and the save dialog are untested until run on Windows

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
