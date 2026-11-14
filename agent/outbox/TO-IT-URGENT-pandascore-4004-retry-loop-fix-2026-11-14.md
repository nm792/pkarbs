# PH #339 PandaScore 4004 safe-restart gate — 2026-11-14 15:33Z

- Restart remains held: tolerant recovery from the open current-hour gzip found 315 status rows; latest rows at 15:33:25Z (match 1786831) and 15:33:26Z (match 1789161) both report `running`. The no-live-match precondition is false.
- Capture PID 548127 is still running (started 13 Nov 17:39:46Z). Restart not attempted; no process was stopped.
- Approved patch remains staged on disk, not loaded by the running process: `live/pandascore/ll_capture.py` SHA-256 `be437551ef871437a0a168f25ef09886dc161569c72060243393bbe8241dc8f7`; byte-identical backup SHA-256 `a6d7d06a962b3eeb86fac6711e6a8a47f7b6358eca7403979732245833d698ba`.
- OPEN / NOT VERIFIED: safe restart and post-restart proof; both wait for fresh data to establish no live match.
