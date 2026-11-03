# Status: sports-mece-shadow

State: RUNNING (bounded re-run in flight, read-only replay, --per-run persisted)
Last heartbeat: 2026-11-03T08:2xZ
Output CSV: /root/sports-mece-shadow-per-run.csv (root fs, 8.9G free; shadow vol 100% full)

## 2026-11-03 morning
- Prior full 7-day run (00:28-06:58Z) EXITED cleanly but without --per-run, so numeric
  P&L/edge was unrecoverable from disk (ran to stdout of departed session; runs.jsonl 7,784
  rows is source data, not results).
- Re-run launched 08:16Z: pid 1213534, `--data
  /mnt/HC_Volume_107257520/pkarbs/shadow/data-v2 --one-way 0.05 --delays 0,1,3,market
  --max-usd 500 --days 9 --per-run /root/sports-mece-shadow-per-run.csv`.
- Bounded load verified: RSS ~65 MB, single process, no OOM. Log /root/sports-mece-resim.log
  (empty while iterating 7,784 runs x 4 delays; CSV written as it progresses).
- DISK: /mnt/HC_Volume_107257520 is 100% full (0 avail) — CSV redirected to /root fs.
- Next on completion: post agent/outbox/shadow-sim-report.md from the per-run CSV.
