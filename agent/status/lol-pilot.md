# agent/status/lol-pilot.md — LoL pilot dry run (DK vs BLG, 5 Nov 22:00Z)
State: RUNNING (dry) — process still up for T1 vs KC (22:00Z today). Data copied per 2026-11-06-copy-now.
Pid: 1559461 (timeout 28800, MemoryMax 512M, DRY ONLY)
Out: /root/lolpilot/out
Data copied (gzipped) to live/lol_pilot/runs/2026-11-05/: pilot.jsonl.gz, books.jsonl.gz, summary.json.gz (840K total, <90MB no split).

## speed_report.py (02:1xZ) — log rows to 00:34:56Z
kill events 39, windows 38, >=1c price-move events 38
delays (s, +ve = after price moved): WS arrival n38 med +17.6 p10 -2.7 p90 +52.1; decision after WS n38 med +0.6; first paper bid after WS n16 med +1.0; CLOB rtt n38 med +0.1; bid accepted after move (sum) n16 med +20.6 p10 -16.9 p90 +54.2
paper bids 62; queue ahead at placement (shares) med 1876 p90 15436; paper fills naive 0, queue-adj 0 on 0 of 62 bids

## live/cs2_pilot/report.py (02:1xZ)
log rows 618 (21:47:30Z to 00:34:56Z); geoblock blocked:false (FI)
games w/ round events 1; round events 39; windows 38; skips 1; map-end/reset skipped 15
orders 62 (310 sh, $202); cancels 62; rejects 0; queue-ahead med 1876; placed 10.8s after WS (median)
fills real $0.00 (0), paper $0.00 (0); resolved markets 0, realized P&L $0.00; halts []
errors: {}; rule checks: bid>=best ask 0, bid below mid x0.975 0
PASS 6/6: geoblock, >=20 round events tier-1, >=10 windows, no bad bid, feed delay >=10 events, no crash
