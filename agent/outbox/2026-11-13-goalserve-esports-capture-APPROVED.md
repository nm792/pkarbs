# 298 — Goalserve esports capture STARTED 2026-11-13 14:04:31Z (APPROVALS item 18; Nick "yes" 13:46Z)

APPROVALS NEEDED: none. Nick's "yes" of 13 Nov 13:46Z is recorded on tt-review `dialogue/APPROVALS.md` item 18 (the file the inbox note calls item 13).

RESULT
- `live/goalserve/capture.py` gained one line `"esports": "/inplay-esports.gz",` — new sha256 `52068242107afaf762a6f72a53d298eee1fd23bab925d6c8413f31f231d51204`; byte-identical pre-edit backup `capture.py.pre-esports-20261113T140357Z` (sha `a975180499ec2eae000f946f8257960f93a3b529528089e1c737122bf5cd68b1`); `python3 -m py_compile` OK. Poll left at 1.0 s — APPROVALS item 18 states "poll stays 1 s unless the reviewer wants v2's ~0.5 s cadence, which is a second edit".
- tmux `goalserve` restarted 14:04:31Z (session killed 14:04:30.5Z); first row after restart `2026-11-13T14:04:35.188+00:00` — capture gap 4.7 s. Session `goalserve` created Fri Nov 13 14:04:31 2026.
- Esports rows live: 32 of 32 new rows carry an `esports` payload, 0 error rows; first payload sha1 `fe07e36310f6fabebc1eb3afe046e3d08d7094d1`, 167,114 B.
- writers.conf row added: `goalserve|/vol2/goalserve|pkarbs/goalserve|-|y|hourly` (backup `writers.conf.pre-goalserve-20261113T140908Z`); `ship_raw.sh --dry-run --only goalserve` reads it and reports "nothing eligible" while today's file is still open, which is correct. Box folder `pkarbs/goalserve`.
- Free space at start: 17 GB available (55%), above the 15 GB floor, so the capture was not stopped. The inbox note's "VOL2 at about 94%" is stale — measured live 14:09Z.

DATA
- `/vol2/goalserve/goalserve_20261113.jsonl` — 23,640,775 B at 14:09:08Z. 60 s measurement 14:05:32Z to 14:06:32Z: +36,455 B, +32 rows → 52.5 MB/day whole-file projection, against ~40 MB/day for the same file before the restart, so ≈ +12 MB/day attributable to the esports field. Payload is not stored: per clause 5 the row keeps only recv_ns, sha1, bytes, changed, first_seen_ns.
- Revert: `cp -p live/goalserve/capture.py.pre-esports-20261113T140357Z live/goalserve/capture.py` then restart tmux `goalserve`; remove the `goalserve` line from `/root/ship/writers.conf` (backup above).

OPEN / NOT VERIFIED
- The clause-5 one-hour MB/day figure is not yet measurable: the hour completes 15:04:31Z. The number above is a 60 s projection, not the one-hour trial.
- No pause hook exists for a tmux capture (no `disk_gate.sh` or `start_writer.sh` on disk) and no trial end date is named in the goalserve task files. Both are left for the reviewer to specify; nothing was invented.
- The ~0.5 s poll cadence of TASK-goalserve-v2 was not applied, as it is a second edit outside the approved single-line change.

Count: notes run 1, outstanding 0, PENDING open 1
