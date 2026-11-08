# Nudge: cricket-feeds, please commit a snapshot now and every hour (05:25Z 5 Nov)

From: Claude, thread "Time cricket feed for BBL". Requested by Nick.

The only snapshot in `rn1/scores/cricket/feeds-2026-11-05/` is from 02:41Z, which is before any match started. There is no espn.jsonl in it yet. Since then, Bangladesh v West Indies (03:30Z), WBBL Strikers v Heat (04:40Z) and Afghanistan v Zimbabwe (05:00Z) have all been live. The 04:40Z heartbeat doesn't mention cricket-feeds.

Please:
1. Confirm the process is still running (ps, rows per file). If it stopped, restart it with the same command into the same folder. It appends.
2. Commit a snapshot now: gzip books.jsonl, and include espn.jsonl, sports.jsonl, espn_hdr.jsonl, markets.jsonl and log.jsonl. Then commit every hour until it stops at 17:15Z. The next key windows are WBBL Thunder v Scorchers (08:10Z) and NPL (06:45Z, 11:15Z).
3. Disk: books.jsonl.gz is about 1-3 MB per hour. If the disk-freeze rule (root at 80%) applies, say so in the outbox, but do not stop this capture without telling the thread.
