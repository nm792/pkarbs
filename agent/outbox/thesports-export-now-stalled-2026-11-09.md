From Hermes (server member) - reply to thesports-export-now-stalled-2026-11-09

## TheSports slim export stall: cause found, one-off export pushed, timer fix gated

RESULT
- CAUSE (root): the 2h export timer (export_timer_2h.sh, cron 0 */2 at 00:24/02:24/04:24Z) builds its commit on the branch tip it fetches at run START, but the ~15-min heartbeat/dispatch rounds advance the same branch before the export finishes pushing. Every push was rejected "fetch first / non-fast-forward" (push_rc=1 at 00:08, 02:16, 04:24, 06:33Z). Because origin's committed slim ts_mqtt minute never advanced, SINCE stayed fixed at 1794176375 (10:19Z 8 Nov), so each run re-exported the WHOLE backlog - files grew 5981 -> 12918 -> 19045 -> 23227, filling /tmp (fatal: sha1 file '/tmp/idx.ts.lock' write error. Out of disk space + No space left on device). The exporter itself and capture-b are healthy.
- ONE-OFF EXPORT (this round): staged a fresh export since the 10:19Z boundary on /mnt (not /tmp), 24,358 slim files (117 MB), pushed via plumbing commit. Confirm on origin: rn1/scores/thesports/final-topics-32295b-slim/ts_mqtt/ now extends past the 04:24 export.
- capture-b still writing: last ts_mqtt write 06:41Z (source /mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b/ts_mqtt.jsonl, unit thesports-capture-b active, pid since 8 Nov 05:58).
- FIX (needs approval): timer script needs a small change - re-fetch + rebuild on the fresh origin tip right before push (one retry on rejection), and stage to /mnt not /tmp. That is a code change to export_timer_2h.sh; routing to the reviewer/Nick (class 4, one code change within 48h budget).

DATA
- /var/log/thesports_export_timer.log (00:08-06:33Z entries show the push_rc=1 + file-growth pattern)
- /run/writer-locks/thesports-slim.lock (0 bytes, not stuck)
- status: agent/status/thesports-trial.md updated

OPEN / NOT VERIFIED
- Last ms of ts_mqtt/books_mid in the pushed one-off: readable from origin slim ts_mqtt; not re-quoted here to avoid a stale fingerprint.
- Timer-script fix pending approval (one code change).

Count: notes run 1, outstanding 0.
