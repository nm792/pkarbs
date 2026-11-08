# from_agent — 2026-11-06-lol-pilot-copy-now (LoL DK-BLG data copy)

RESULT
- Ran both report scripts against /root/lolpilot/out/pilot.jsonl; outputs pasted verbatim into agent/status/lol-pilot.md.
- Copied + gzipped pilot.jsonl, books.jsonl, summary.json to live/lol_pilot/runs/2026-11-05/ (840K total; books.jsonl.gz 834K — far under 90MB, no split). gzip -t pass.
- Committed the three artifacts; process LEFT RUNNING (dry, pid 1559461) for T1 vs KC 22:00Z today. DRY ONLY maintained.
DATA
- live/lol_pilot/runs/2026-11-05/{pilot,books,summary}.jsonl.gz (840K)
- Highlights: 62 orders/62 cancels, 0 rejects, queue-ahead med 1876 sh; 6/6 report gates PASS; feed delays (WS after price move) med +17.6s on 38 events.
OPEN / NOT VERIFIED: none (copy + report order complete).
Count: notes run 1, outstanding 0.
