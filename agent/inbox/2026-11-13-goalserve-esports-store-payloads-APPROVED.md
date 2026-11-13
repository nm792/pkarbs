# To Hermes and IT: store changed esports payloads NOW (Nick approved)

Nick said "yes" at 2026-11-13 14:43:42Z to this exact question: store the changed
esports payloads (gzipped, esports only, same 15 GB free-space floor, auto-stop if breached).

## Why
The esports capture stores only recv_ns, sha1, bytes, changed, first_seen_ns. That cannot say
which team won a round or took a kill, so the feed standard
(feeds/STANDARD-feed-latency-test.md) cannot line a Goalserve event up with the Polymarket
price. Needed before the LoL final.

## Do
1. In live/goalserve/capture.py, for the esports poll ONLY: when sha1 differs from the previous
   poll, also write the raw body, gzipped, with recv_ns, to /vol2/goalserve/esports_payloads/
   (e.g. one .jsonl.gz per hour, one line per change: recv_ns + body). Other sports unchanged.
2. Keep a revert copy first. Check free space before every write; stop writing payloads and log
   it if free space is under 15 GB. Do not stop the existing hash/size capture.
3. Add the new folder to the hourly box sync if writers.conf needs it.
4. No credentials in the repo or in the payload files' names or headers.
5. Update agent/status/goalserve.md at once: time live, sha256 of capture.py, first
   changed-payload row, bytes per change, and MB/day projection (measure over 10+ minutes,
   not one minute). Add the 15:04:31Z one-hour hash-capture figure too.
6. Confirm the first stored payload parses and shows the team names, round and kill fields.

IT: if Hermes' task loop is idle, apply this directly; this is the top item in the queue,
ahead of everything else for PK arbs. Reply on #295.
