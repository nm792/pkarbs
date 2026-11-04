# GEN-LYON capture check (4 Nov 21:50Z)

GEN-LYON starts 22:00Z. heartbeat 21:30Z does not mention lol-live-capture running, and there is no server-GEN-LYON/ in the repo yet.

Please (PROTOCOL-bounded job, same as TES-IG: one process, 600 MB cap, ends +150 min after the last game):
1. Confirm capture.js for GEN-LYON is running (`ps`), from the merged version (2 s polls, startingTime fix, 15-level books, sports WS logging -> GEN-LYON_sportsws.jsonl).
2. If not running, start it now the same way as TES-IG.
3. Copy outputs to rn1/scores/lol/live-2026-11/server-GEN-LYON/ every 30 min, and write agent/status/lol-live-capture.md with start time and line counts.

A cloud backup (sports WS + Riot feed, all 5 games) is running from the thread side.
