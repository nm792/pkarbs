# Nick APPROVED the export_timer_2h.sh change (card answered 09:28Z 9 Nov)

Approved change: right before each export push, re-fetch origin, rebuild/re-apply the export on the fresh tip, push, retry once on rejection; stage files under /mnt, not /tmp. Nothing else in the script changes. Deletion guard stays on every path.

Please make the change, dry-run it once, and say in the outbox: commit, dry-run result, last `ms` in markets.jsonl and log.jsonl of the next export. Also still open: full current markets.jsonl (thesports-markets-full-export-2026-11-09.md), the 9 Nov diary refresh, and the cause of 39267eef0.
