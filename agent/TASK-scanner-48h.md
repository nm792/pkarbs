# TASK-scanner-48h — PROPOSED (not open; waiting for Nick's go-ahead)

One question: do Polymarket-tradeable MECE edges (synthetic covers, negRisk sets, time ladders) appear often enough and last long enough to act on? Kalshi pairs are logged alongside as alert-only.

## Before starting
- `python3 scanner/test_scanner.py` must print `16/16 gates pass`.
- No other OPEN task (PROTOCOL.md rule 5).

## Run (single process, bounded)
```
systemd-run --user --scope -p MemoryMax=256M -p RuntimeMaxSec=176400 \
  python3 scanner/run.py --minutes 2880 --poll 60 --venues pm \
  --log reports/scanner/alerts.jsonl --snapshots reports/scanner/snapshots.jsonl
```
Stop early if RSS exceeds 200 MB or more than 20% of polls fail in any hour.

## Pass/fail, fixed now
Health (all three must hold, otherwise FAIL and no conclusions):
- H1: ≥ 95% of polls complete.
- H2: no alert is ever opened on a structure whose guards listed `crossed` or `stale` in the same poll (check `snapshots.jsonl`).
- H3: the Senate family structures are priced in ≥ 95% of polls.

Result (reported either way, from `alerts.jsonl`):
- PASS if ≥ 1 TRADEABLE alert with ≥ $5 profit at ≥ 0.5c edge stays open ≥ 15 min.
- Otherwise Polymarket-only is too thin for now.

## Deliver
`reports/scanner/2026-10-XX.md` must include: alerts by structure (count, total and median duration, peak profit), alert-only Kalshi pairs reported the same way, and the gaps between alerts. Also commit `alerts.jsonl` and `snapshots.jsonl`, gzipped. Clean up the process and temp files afterwards.
