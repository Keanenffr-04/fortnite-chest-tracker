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
- [ ] YOU: run the benchmark and record real samples (see README)
## v1.1.3 - Detection engine v1 + debug view
## v1.1.4 - Event validation + replay tests
## v1.1.5 - Overlay
## v1.1.6 - Hotkeys, sound, click-through
## v1.1.7 - Dashboard + Live Tracker page
## v1.1.8 - Statistics, charts, match history
## v1.1.9 - Settings UI, CSV export button, auto match detection (experimental)
## v1.1.10 - Packaging (.exe), release ZIP, real-gameplay test guide
## v1.2.1+ - Accuracy tuning on real gameplay, bug fixes, optimisation

## Known limits
- No chest detection exists until v1.1.3, and it needs real Fortnite samples from you.
- Fortnite should run in Windowed Fullscreen for the overlay to show.
