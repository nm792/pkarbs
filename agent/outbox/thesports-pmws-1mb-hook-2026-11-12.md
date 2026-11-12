# Outbox reply: thesports slim pmws breached the 1MB pre-push hook (12 Nov 2026)

Reply for: recurring export strand (OPEN 14b / row 13 precedent). Filed 2026-11-12 ~12:50Z.

## What was measured
- The 07:30Z export landed on origin (29254c153, +28,721 files; newest slim ts_mqtt chunk 1794461599 = 07:30Z; HEAD == origin, tree diff empty).
- The 10:00Z slot built to commit 4cfdf5a0 (+11,904 files @11:11:36Z) but the push was REJECTED by the repo pre-push hook: `rn1/scores/thesports/final-topics-32295b-slim/pmws.jsonl.gz = 1,056,835 bytes (raw over 1MB); box+manifest route only`. The whole push failed (hook is all-or-nothing), so 10:00Z and 12:00Z slots strand.
- pmws.jsonl (VOL2 source) is 28,534,117 B; gz level-6 = 1,206,552 B, gz level-9 = 1,090,771 B — both over 1,000,000, growing ~150 KB gz/hour. Recompression level cannot fit it.

## Fix applied (Type A export plumbing, per row 13 precedent: skip only the file that breaches)
- `live/thesports/export_slim_32295_plumb.py`: after writing each flat cumulative (`markets.jsonl.gz`, `pmws.jsonl.gz`, `ts_poll.jsonl.gz`, `log.jsonl.gz`), if the gz is >950,000 B the file is SKIPPED from the push with a printed WARN; the rest of the export pushes normally. Raw rows stay on VOL2 (the capture store, untouched). Revert: restore `export_slim_32295_plumb.py.pre-pmws-20261112T1245Z`.
- Backup: `.pre-pmws-20261112T1245Z`; new sha 0xdc5e968a6…; python3 -m py_compile PASS.
- The in-flight 12:00Z-slot build (started ~12:08Z) invokes the exporter from the current path, so it picks up the fix at its export step and should land on origin ~13:10Z (verify next dispatch).

## OPEN for the project to rule (project-channel decision, not a blocker)
- pmws on origin freezes at the last sub-1MB copy until the project picks a durable route: (a) split pmws into ≤900 KB gz parts (consumer concats in order, same pattern as ts_mqtt chunks), or (b) ship pmws to the storage box with a manifest row in git (hook's own "box+manifest route"). Either is a one-script change; no data is at risk meanwhile (VOL2 holds the full file).

Count: notes run 1, outstanding 1 (project ruling on pmws route), PENDING open 0
