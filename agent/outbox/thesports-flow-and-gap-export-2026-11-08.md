# Outbox: TheSports MQTT flow confirmed + gap slim committed (2026-11-08T01:0xZ)

Reply to `agent/inbox/thesports-flow-and-gap-export-2026-11-08.md`. Read-only executed; nothing deleted.

**1. MQTT flow confirmed (live chunk `final-topics-32295b`, first_ts 1794098342431 = 07T23:19Z)**
- ts_mqtt is LIVE and receiving on all topics. Rows by topic: basketball 15,246 · dota2 1,287 · tennis 898 · csgo 271 · lol 106 (total 17,808 @ ~01:00Z).
- No topic silent; lol is the smallest but present (106). books (22,754→growing), pmws 333, markets 181 KB.
- Single instance running (pid 279116x, chunk final-topics-32295b, spool /vol).

**2. Gap slim committed — `rn1/scores/thesports/final-topics-32295-slim/` on claude/project-thread-vg2ckg**
- Coverage: 14:00Z–16:00:13Z (final-topics-32295 tail after the committed slim-1102), books_mid 420,817 rows, ts_mqtt 261,695 msgs, 181 per-minute parts + 9 books_mid parts, max part ~521 KB (all < 5 MB hook).
- Layout mirrors slim-1102/final-topics-8917-slim: `books_mid/<hour_ms>/<bucket_sec>.jsonl.gz` ({ms,tk,bb,ba,q}), `ts_mqtt/<hour_ms>/<minute_sec>.jsonl.gz`, plus markets/pmws/log/ts_poll `.gz` and `counts.json` (topic|hour).
- Raw books.jsonl / ts_mqtt.jsonl untouched (still live in /vol).

**3. Standing 2 h export** for `final-topics-32295b` — not yet scheduled as its own job; I'll flag the cadence in the status file and can arm the recurring capture+commit if the reviewer confirms it should run unattended (external-cost/none, code-side only if a new job is needed).
