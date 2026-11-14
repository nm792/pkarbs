# #339 PandaScore retry-loop safe-restart recheck — 2026-11-14 15:53Z

- Restart remains held: the no-live-match precondition is false. The active capture process (PID 548127) remains running; no process was stopped.
- Tolerant read of the append-streamed 15:00Z gzip recovered 643 complete rows before EOFError on the open stream. Latest status rows: match 1786831, `match_status=running`, `game_status=running`, updated 15:53:13Z; match 1789161, `match_status=running`, `game_status=finished`, updated 15:52:24Z. The match-status field still reports both as running, so the restart gate is not satisfied.
- The approved code remains staged, not live; the running process predates the staged file. No code or process changes were made. No data was deleted.
- OPEN / NOT VERIFIED: safe restart and post-restart behavior, held until a fresh source read establishes no live match.
