# Status: nba-feed-delay (live NBA feed-delay capture, night 4-5 Nov)
State: capture RUNNING (restarted 2026-11-04T23:47Z, PID 1781643, `timeout 27000`, MemoryMax 300M scope). Poll.py sleeps to 23:50Z then threads per live game; exits 06:45Z.
Correction: a prior status line read "RUNNING" with 0 rows, but no nba process was present at 23:46Z — the capture was not actually up. Restarted from the task spec's sanctioned command. Window 5 Nov 00:00-03:30Z games, exits 06:45Z.
Rows: 0 /root/nbacap/out-2026-11-05/espn_plays.jsonl  0 nba_actions.jsonl  0 polls.jsonl  0 log.jsonl (0 bytes; poll.py pre-created at 07:17Z, appends from 23:50Z).
Polls HTTP: (none yet — first polls at 23:50Z). First real check + copy 00:15Z per task.
Poll storm: 0 (will monitor).
Coverage: cs2-ws-logger (PID 426344) carries the Polymarket NBA side through 06:45Z — confirmed alive.
Next: copy out/* to winmodels/raw/nbacap-2026-11-05/ every 30 min; check 00:15Z for 403/429 storms; cleanup + confirm process gone at 06:45Z.
waiting for Nick: none — read-only capture, runs directly.
