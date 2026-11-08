# thesports-trial status
state: running (capture-b scope active, writing ts_mqtt/books)
last heartbeat (UTC): 2026-11-08 19:22Z (server-member sweep round)
export: 2h timer cron '0 */2 * * *' armed; guard installed (09:39Z card), plumbing-only exporter adds ONLY slim dir, aborts empty manifest, never -A. Last slim chunk 18:07:23Z +7189 files landed on origin; exports continuing on the 2h timer.
auth: ssh key nm792 verified 12:57Z.
process: thesports-capture-b.scope active; books.jsonl.gz updating continuously (mtime 19:22Z). RSS under 650 MB cap, VmSwap 0 — no OOM (monitor 'oom' flag confirmed stale/noise).
errors: none this round.
output: rn1/scores/thesports/diary/*-2026-11-08.json; slim final-topics-32295b-slim markets/log full on origin.
