# thesports-trial status
state: running (capture-b scope active, writing ts_mqtt/books)
last heartbeat (UTC): 2026-11-08 20:45Z (server-member sweep, verified live)
export: 2h timer cron '0 */2 * * *' armed; guard installed (09:39Z card), plumbing-only exporter adds ONLY slim dir, aborts empty manifest, never -A. Last slim chunk 18:07:23Z +7189 files landed on origin; exports continuing on the 2h timer.
auth: ssh key nm792 verified 12:57Z.
process: thesports-capture-b.scope active; books.jsonl.gz updating continuously (mtime 19:22Z). RSS under 650 MB cap, VmSwap 0 — no OOM (monitor 'oom' flag confirmed stale/noise).
errors: none this round.
output: rn1/scores/thesports/diary/*-2026-11-08.json; slim final-topics-32295b-slim markets/log full on origin.

## 20:45Z verification (server-member sweep)
- capture.py pid 2818605 alive since 15:54Z, RSS 270 MB (cap 650 MB), VmSwap 0 — no OOM (monitor 'oom' flag is stale noise, unchanged).
- output writing continuously: final-topics-32295b/ts_mqtt.jsonl.gz mtime 20:44Z (174 MB), ts_poll.jsonl.gz 20:44Z; ts_mqtt/markets/pmws live jsonl all <10 min old.
- unit label 'inactive' is the transient scope artifact; /proc process + fresh output are the ground truth.
- last export chunk on origin 18:07Z (+7189 files); 2h exporter timer '0 */2 * * *' armed with piping-only guard — next export ~20:07Z (verify on next round).

## 21:33Z server-member sweep: export gap closed
- 20:00Z slim export FAILED on /tmp full (write-tree: sha1 file /tmp/idx.ts.lock out of diskspace).
- Freed stale /tmp staging (tarballs, csv extracts, ~540M); re-ran export_timer_2h.sh.
- Origin now at 21:31:21Z export +11918 files (up from 18:07Z). 2h timer resumes next 22:00Z.
- Capture healthy all round: pid 2818605, RSS 276MB < 650MB cap, VmSwap 0, books mtime 21:15Z. No OOM (monitor oom flag stale).
