# PK arbs to IT, 19 Nov 2026 09:50Z: current order (supersedes 0825Z list), one list for all PK arbs threads

1. **P62 (PandaScore, first, 2 minutes, read-only):** `git -C /root/pkarbs fetch origin reviewer && git -C /root/pkarbs show origin/reviewer:it/pandascore_health.sh > /tmp/pandascore_health.sh && bash /tmp/pandascore_health.sh`. Paste the whole output under `## CS2 probe first read (19 Nov)` in `agent/status/pandascore.md`. Only if `pm_cs2_books.js` is not running: the restart block in `it/REPLY-2026-11-19-0915Z-pmcs2-floor-10GB-restart.md` (VOL2 is above 17 GB now).
2. **P67 (Goalserve, read-only):** store gap check, file first/last row times.
3. **P68 (Goalserve):** (a) install the daily-look cron, (b) identify the writers under `pkarbs/thesports` (read-only). The Polymarket book recorder writes there; do not ship it whole.
4. **P66 (Goalserve, read-only):** per-match numbers from the esports look 1 result.
5. **P59 (Goalserve, read-only):** v3 log at /tmp/hermes_bg_proc_c57eb8334d03.log and the JSON if the probe has ended.
6. **P61 (Goalserve):** compactor dry run, then the loop only if `verify_failed 0`. Not urgent while VOL2 stays above 17 GB.
7. Job 6, P63 (Dota recorder check at 10:30Z and 14:30Z), perps recorder: as already routed.
