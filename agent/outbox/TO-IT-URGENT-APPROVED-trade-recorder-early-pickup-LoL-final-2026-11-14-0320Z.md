# Reply to #317 — early pickup of the LoL Worlds final markets (Nick approved 03:13:59Z)

Posted 14 Nov 04:22Z. P12 item (2). Proof items 1 and 2 below are due 06:00Z and are answered early; items 3 and 4 are due 12:00Z and 17:00Z and are listed with their exact times.

## 1. Change applied — ALREADY LIVE, no further restart needed (proof by 06:00Z)

- **The one line** (`live/thesports/capture.py`, `discover_pm()`):
  - before: `if not (st - 1200 <= time.time() <= st + 6 * 3600): continue   # 20 min before start to 6 h after`
  - after: `if not (st - 28800 <= time.time() <= st + 6 * 3600): continue   # 8 h before start to 6 h after (early pickup, inbox TO-IT-URGENT-APPROVED-trade-recorder-early-pickup-LoL-final-2026-11-14-0320Z)`
- **Backup / revert:** `live/thesports/capture.py.pre-lead8h-20261114T0335Z` (byte copy of the pre-edit file; restore it and restart the capture to revert). `py_compile` OK, sha256 `9dbb4f878a3f2527f2bc8c48…`.
- **It was already running before I read the note:** the edit landed on disk at **03:28:58Z**, and the guard's own restart put a fresh process on it at **03:30:03Z** (pid 2489797, `systemd-run --unit=thesports-capture-b`), i.e. 65 s after the edit — so the running capture already carries the 8-hour lead. **I did not restart it again** (a second restart would only add a gap for no change).
- **Proof from output, not from the file:** at **03:30:04Z**, one second after that start, `markets.jsonl` registered 87 markets whose start is **more than 20 minutes ahead** — cricket 04:40/05:00/06:30, CS2 08:00/09:00 (27–287 minutes ahead). The old 20-minute window could not have registered a single one of them; the running code is the new line.
- **Commit:** this reply and the code change are pushed together on `claude/project-thread-vg2ckg` (SHA in the commit that carries this file) — the change was on disk but uncommitted before this.

## 2. Are the Worlds final markets in markets.jsonl? (proof by 06:00Z)

**Not yet — 0 rows**, measured 04:20Z: `markets.jsonl` (3,479 rows, newest 04:00:53Z) holds no market with start `2026-11-14 19:00`. Expected first registration: **11:00Z**, the moment the 8-hour window opens (19:00Z − 8 h), provided gamma lists the final by then; that is 3 h inside the note's "certainly on by 14:00Z" bar. Registration time will be read straight off the row's `ms` field and appended here when it lands.

## 3. Fresh trade and book rows for the final — due 12:00Z

Not yet due and not yet possible (the markets are not registered; see 2). The recorder pair is live now: capture `thesports-capture-b` pid 2489797 and the PM trade recorder `pm_trades_capture.py` pid 2271688, both writing to the data volume.

## 4. Same again plus data-disk free space — due 17:00Z

Not yet due. Data volume measured 04:10Z: 72,001,667,072 B free of 105,089,261,568 B (28% used).

Key material: none in this reply. No IP, host name or account written.
