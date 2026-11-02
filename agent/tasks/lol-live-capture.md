# TASK: live LoL capture for Worlds 3-6 Nov 2026 (livestats + Polymarket book)

Owner thread: "Capture live LoL game data" (branch claude/project-thread-836e0s). Written 2 Nov 2026.

## Question (one only)
Within the scheduled windows of the four Game 1s (TES-IG 3 Nov, GEN-LYON 4 Nov, DK-BLG 5 Nov, T1-KC 6 Nov, scheduled 22:00 UTC each), how much later does the Polymarket Game 1 winner price move after each Riot livestats event, measured on the book (1 s REST polls) and on trades?

## Pass / fail, fixed before running
- PASS for the capture: at least 3 of 4 matches have frames for at least 90 percent of their 10 s cadence and at least 80 percent of 1 s book polls succeed (no 429 storms).
- FAIL: fewer than 3 matches meet both. Then report which matches failed and why; do not report lag figures.
- No P&L. Lag figures are reported as a distribution with n events and the threshold used (2c move vs the last trade before the event).

## Inputs
- config.json: game 1 IDs, Polymarket condition IDs and token IDs, and scheduled start times. Resolved 2 Nov from getEventDetails and gamma.
  - Check each Polymarket title against the schedule before running. Polymarket slug dates are not match dates (DK-BLG slug says 11-03, schedule says 11-05).
- No API key is needed for the capture itself. The esports key is only needed to re-resolve game IDs, so pass it in env LOL_API_KEY and do not commit it.

## Protocol (agent/PROTOCOL.md)
1. Local test done 2 Nov: capture.js ran 60 s against a completed game (frames 10 lines, book 7 changed rows). Not yet run on a live match.
2. Bounded: each match runs in its own window (scheduled start minus 90 min to plus 150 min). Memory cap 600 MB via systemd-run where available. One process per match.
3. Clean up after each window: confirm processes are gone with `ps` and `free -m`, then say so in the report.
4. Copy outputs (`*_frames.jsonl`, `*_books.jsonl`, `*_capture.log`) to /mnt/project-files/rn1/scores/lol/live-2026-11/ every 10 min during the window, not only at the end. Commit the final copy to the repo.
5. Post status to the thread about every 10 minutes during a window. Never go silent.

## Known limits (state them in the report)
- The WS market channel (ws-subscriptions-clob) returned non-101 from the sandbox on 2 Nov, so books are REST polls at 1 s. The poll step bounds the lag resolution from the book side at about 1 s.
- Trades (data-api /trades, per second) remain the better lag clock after the match.
- livestats timestamps can trail the broadcast. Report the lag distribution and who traded first, and do not call it broadcast latency.
