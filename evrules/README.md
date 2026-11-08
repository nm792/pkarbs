# evrules: per-sport win probability and EV rules

Notes: /mnt/project-files/ev-rules/NOTE-ev-rules-2026-11-02.md

- `ev.py`: fee, rebate, EV, sizing and risk caps (shared).
- `rules.py`: `on_event(sport, before, after, anchor_mid, book)` returns a Decision. Per-sport thresholds are in `RULES`.
- `cs2.py`, `cricket.py`, `rugby.py`: the sport models. The LoL model is in `rules.lol_fair`.
- Fitting and tests (they write `params/*.json`):
  - `python3 -m evrules.fit_lol` fits the level model (reference only).
  - `python3 -m evrules.fit_lol_events` fits the event-jump model used for trading.
  - `python3 -m evrules.eval_cs2` runs the round-change test and fits the shrink.
  - `python3 -m evrules.fit_cricket <unzipped cricsheet dir>`
  - `python3 -m evrules.fit_rugby <espn scoreboard dir>` (raw data is in ev-rules/raw/).
- Checks: `python3 -m evrules.test_evrules`
