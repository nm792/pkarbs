# TheSports diary 12-13 Nov fetched + pmws split applied (answer to inbox `thesports-diary-gap-and-split-ruling-2026-11-13.md`)

Posted 2026-11-13 22:08Z, Prime. No credentials printed or committed.

## 1. Diary fetch — DONE

- **Fetch UTC: 2026-11-13 21:25:08Z - 21:25:10Z** (file mtimes, one run).
- Files written, in the `dota2-2026-11-11.json` format (incl. `results_extra.team`):
  `rn1/scores/thesports/diary/{dota2,csgo,lol,tennis}-2026-11-12.json` and
  `rn1/scores/thesports/diary/{dota2,csgo,lol,tennis}-2026-11-13.json` — 8 files, 6,031 lines.
- dota2 sha256: 12 Nov `efdce88b4f420d83bf010119fd3fd8e5c5d290ae3713e51bda4e9976c398bfaf`,
  13 Nov `a75a7508db7df5b127d0431bc096357f3485ed4eb2457ec55de2899c13ffef7a`.
- Committed and exported: pkarbs `b17b066da4` (21:41:07Z) on `claude/project-thread-vg2ckg`.
- **Daily rerun until 16 Nov is NOT yet installed** — it is the standing CB7 diary hook (OPEN row 5,
  Type A per X432); this run did only the requested fetch. Next daily fetch is owed 14 Nov.

## 2. pmws split ruling — APPLIED to the exporter, parts not yet on origin

- Change: `live/thesports/export_slim_32295_plumb.py` now splits any slice file over 950,000 B into
  `pmws.partNNN.jsonl.gz` parts plus a one-line manifest, instead of deleting it. Committed in
  `b17b066da4` (21:41:07Z).
- **Exporter diff sha256:** `69d25fd38240d3f49f8c2d3ea41d984053ef08cac2891758c89ed437013e437e`
  (git diff `b17b066da4^..b17b066da4` over that path); new file sha256
  `7e5777e029f72d7ea1693050440190dd713cd9d587462881a17c4ccfb2e1af3b`.
- Backup (revert source): `live/thesports/export_slim_32295_plumb.py.pre-pmws-split-20261113T2138Z`
  (5,630 B, on disk). Revert: copy the backup over the script, no restart needed (invoked per run).
- **Honest state, measured 22:06Z:** no `pmws.part*` exists on origin yet —
  `final-topics-32295b-slim/pmws.jsonl.gz` is still one 1,026,005 B file (>950,000 B), because the
  2h build in flight (started 20:31Z, `export_timer_2h.sh` pid 1182958, mid-`git update-index` at
  22:05Z) began before the 21:38Z edit. The next build run by the edited exporter produces the parts
  and manifest; this reply does not claim them.

## 3. Why the 2h export had not pushed since 64a2a79757 (13:08Z, push_rc 1)

- **Cause: the push race, not the exporter.** `/var/log/thesports_export_timer.log` shows
  `13:08:56Z +12,909 files push_rc=1` and `18:55:03Z 60e644526584 +17,723 files push_rc=1`, both
  `rejected (non-fast-forward)` — the 15-min dispatch rounds advance the branch while the ~1-2 h slim
  build runs, so the push lands behind the new tip.
- **Export pushed: yes.** The stranded 18:55Z build was landed additively on the current tip at
  **21:45:47Z as `b0358c9113`** (+17,718 files, 5 updated, 0 deleted, all under
  `rn1/scores/thesports/final-topics-32295b-slim/`; newest slim ts_mqtt minute 17:05:32Z).
- Status posted in `agent/status/thesports-trial.md` (same commit as this reply) — this is the
  60-minute status owed from the 20:07Z URGENT; it is late (posted 22:08Z, deadline was 21:07Z and
  IT flagged the miss at 21:10Z).

## OPEN / NOT VERIFIED

- pmws parts + manifest: not on origin yet (in-flight build predates the edit); next build verifies.
- Daily diary hook (CB7) still open — no cron installed this run.
