# To IT, 18 Nov 2026 ~14:15Z: URGENT, locate and restore the 16-17 Nov Dota raw capture (answer due 16:00Z today)

1. **Goal.** Measure Valve's live-feed delay per Dota league against the Polymarket price. Nick's instruction (18 Nov 14:10Z): "get it restored with IT".
2. **Measured position.** No delay result exists. Hermes status (agent/status/dota-live-capture-2026-11-16.md, commit fd49c32afd) says `$HOME/dotacap/out-2026-11-16` is absent. **That path was my error in the task file, not necessarily a deletion.** The publisher script (agent/tasks/dota-live-capture-2026-11-16-publish.py, commit daf1447d67) shows the capture output was at `/vol2/pkarbs/dotacap/run-2026-11-16/out`, with chunks in `/vol2/pkarbs/dotacap/run-2026-11-16/publisher/chunks`. The final report (commit c5dc7dfd05) says "Local output remains outside Git" with final counts: books 107,624, league_games 15,904, opendota_live 2,723, realtime 145,268, rt_polls 325,064, sportsws 7,158 rows.
3. **Most important item: check `/vol2/pkarbs/dotacap/run-2026-11-16/` first.** It may all still be there.

## Please answer yes/no per route, with file names, sizes and row counts or commit, by 16:00Z today
- **R1. Local output** `/vol2/pkarbs/dotacap/run-2026-11-16/out/*.jsonl`: present? sizes, `wc -l` per file (compare to the counts above).
- **R2. Local chunks** `/vol2/pkarbs/dotacap/run-2026-11-16/publisher/chunks` and `manifest.tsv` (75 chunks, 562,819 rows, 288 MB gz, manifest commit 53daee4ac2, covers to 17 Nov 02:42:56Z): present? Checksums match manifest/dotacap-2026-11-16.tsv?
- **R3. Storage box** `pkarbs/dotacap-2026-11-16`: the 75 chunks that transferred before the auth failures. Listing and checksums vs the manifest.
- **R4. Any other copy** on /mnt/HC_Volume_107257520 or elsewhere (`find / -name 'realtime*.jsonl*' -newermt 2026-11-16 2>/dev/null`; read-only).
- **R5. Provider snapshot/backup** of the server or volume (Hetzner) covering 16-17 Nov: does one exist? If restoring needs Nick's account, state the single exact step for Nick.
- **R6. Filesystem undelete**: only if R1-R5 fail and a deletion actually happened. **Stop writing to that disk area until checked.** Say what was deleted, when, and by what command/job.

## Then, if any route has the data
Run the analysis at once: `python3 winmodels/dota/livelag/lag.py <captureDir> agent/tasks/dota-live-capture-2026-11-16/config.json out_lag_2026-11-16.json` (use the real directory; the config file is on origin/claude/project-thread-vg2ckg, run from a clean export), single process, memory cap, push only the small result files.

If nothing can be recovered, give one line per route saying why. Also tell us what removed `out/`, if it was removed.

Confidence 8/10: the paths come from the publisher script and the final report, not from looking at the server. IT's check settles it.
