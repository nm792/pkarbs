# Fleet heartbeat — 2026-11-12 ~02:1xZ (cron sweep)

- Live captures both running: thesports capture-b (final-topics-32295b spool, ts_mqtt/books growing at 02:12Z) and thesports-capture-cricket (scope active, timeout 172800). Slim exports by the 2h timer.
- CB9/10/11 recorders live (netflix/charts/mentions). Netflix 600s TimeoutStart flagged earlier; self-heals per Restart=always.

**FLOOR BREACH — VOL2 UNDER 15G (OPEN row D).**
- VOL2 `/mnt/HC_Volume_107257520` (98G) is **6.3G free, 94% used** — below the clause-8 15 GB floor since 19:52Z 11 Nov; this drive was not listed in the heartbeat before.
- Dominant consumer: `/mnt/HC_Volume_107257520/pkarbs/shadow/data-v2` = **64G** raw sim daily files (186 files, 20261024→20261104) — NOT on the storage box (box `pkarbs/` holds only 17 raw files through 2026-10-24 05Z). writers.conf's `pkarbs` row points at `shadow/data` (empty), not `data-v2`, so the backlog has no box route and cannot be deleted locally yet.
- Also: thesports final-topics-32295b raw spool 16G + 32295 2.4G (live capture; clause-2 hourly-gzip-to-box route needed before local delete).
- Action: needs a writers.conf row for `shadow/data-v2` (and thesports raw) to stage→box, sha-check→delete; a config change → CHANGE-BATCH / reviewer. Flag recorded so the floor is not silently crossed.

Drives: / 50% (18.1G free), /mnt/...107247271 65% (16.7G free), VOL2 94% (6.3G free, FLOOR BREACH).

UTC: 2026-11-12 ~02:1xZ.
