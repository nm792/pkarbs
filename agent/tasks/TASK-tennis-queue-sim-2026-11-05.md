# TASK: tennis OddsPapi history for 5 Nov (to /vol2) + queue-aware backtest, computed result only

From the PK arbs project thread, 5 Nov 2026 17:55Z. Status: OPEN. Supersedes TASK-oddspapi-tennis-nov5 (that one only got 25 files and the old 8:53Z window). Under CHARTER 383: counts as ONE task toward the 2/day budget. No raw data in git. LoL DK-BLG 22:00Z has priority; if it conflicts, skip and say so.

## Question
Do bookmaker (Pinnacle / bet365) price steps give fills on Polymarket tennis once queue position is modelled? The first run had only 7 paired matches (Pinnacle: 0 fills). We need >= 20 paired Pinnacle matches. The recorder has run since 05:32Z (three runs: root, HC, tennis-books-v2 on /vol2 to ~21:30Z), so more matches are now covered.

## Steps (run AFTER the tennis-books-v2 recorder stops, ~21:30Z; one bounded job; each step through /root/bin/disk_gate.sh, a refusal is final)
1. `git pull`. Everything below writes to /vol2 (e.g. /mnt/HC_Volume_107257520/pkarbs/tennis-queue/), never `/`.
2. OddsPapi history, free endpoint, ~2 billable calls:
   `systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 timeout 3300 python3 live/oddspapi/pull_hist.py <VOL2>/oddspapi 2026-11-05T00:00:00Z <NOW-ISO-Z> --max-fixtures 400`
   (tennis plus esports fixtures are kept; fine.) Never log or commit the key.
3. Queue-aware backtest. Collect ALL books and markets files from the three recorder runs (books.jsonl.gz or books.jsonl, markets.jsonl[.gz]); pass them comma-separated, in any order:
   `PK_RAW=<VOL2>/pmraw OUT=<VOL2>/out_queue_sim.json python3 winmodels/tennis/hist/queue_sim.py <VOL2>/oddspapi <books1,books2,...> <markets1,markets2,...>`
   (`<VOL2>/oddspapi` must contain `hist/`. PK_RAW keeps the PM trades cache on /vol2. The script prints "matches paired with recorded books N". Memory-cap it like step 2; if it needs more than ~1.5 GB RAM, say so and stop.)
4. Commit ONLY `out_queue_sim.json` (copy to `winmodels/tennis/hist/out_queue_sim_nov5_full.json`) plus a manifest line (file names, sizes, row counts, time range). No raw, no tarballs (charter 383). Raw OddsPapi files stay on /vol2 and ship to the box with the hourly ship.
5. Delete nothing else. Report in agent/status/tennis-queue-sim.md and agent/outbox/2026-11-05-tennis-queue-sim.md: the "matches paired" count, the full printed result lines, disk figures before/after, gate answers.

## Pass / fail, fixed before running
- PASS: queue_sim finishes and prints pinnacle and bet365 result lines; paired Pinnacle matches >= 20 gives a verdict, fewer is reported as "anecdotal".
- FAIL: anything else: last 20 log lines, retry at most once.
