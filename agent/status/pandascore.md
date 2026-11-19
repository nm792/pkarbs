
## #339 safe-restart gate recheck — 2026-11-14 15:13Z

- Approved patch remains staged only: `live/pandascore/ll_capture.py` SHA-256 `be437551ef871437a0a168f25ef09886dc161569c72060243393bbe8241dc8f7`; byte-identical backup `live/pandascore/ll_capture.py.pre-339-20261114T135600Z`, SHA-256 `a6d7d06a962b3eeb86fac6711e6a8a47f7b6358eca7403979732245833d698ba`. Compile passed in prior verification.
- No-live-match gate is not met. Tolerant read of the append-streamed current-hour file recovered two latest status rows: match 1786831 `running` at 15:12:55Z and match 1789161 `not_started` at 15:12:45Z. Earlier current-hour rows also include live matches. Restart not attempted.
- Capture process PID 548127 remains on the pre-edit version (started 13 Nov 17:39:46Z). The 4004 retry loop for match 1789154 remains visible in the event log; the approved fix is not live.
- OPEN / NOT VERIFIED: safe restart and post-restart behavior. Recheck only when the source advances; restart only after the approved no-live-match condition is established.


## #339 safe-restart gate recheck — 2026-11-14 15:23Z

- Approved patch remains staged only: `live/pandascore/ll_capture.py` SHA-256 `be437551ef871437a0a168f25ef09886dc161569c72060243393bbe8241dc8f7`; backup `live/pandascore/ll_capture.py.pre-339-20261114T135600Z` SHA-256 `a6d7d06a962b3eeb86fac6711e6a8a47f7b6358eca7403979732245833d698ba`. No code changed.
- Restart gate still fails: tolerant read of the open 15:00Z gzip has latest status rows at 15:23:35Z for matches 1786831 and 1789161; both report `running`. Restart not attempted.
- Capture PID 548127 remains on the pre-edit process (started 13 Nov 17:39:46Z). Match 1789154 continues producing code-4004 closes every ~10 seconds through 15:23Z.
- OPEN / NOT VERIFIED: safe restart and post-restart behavior. Recheck only after fresh data establishes no match is live.


## #339 safe-restart gate recheck — 2026-11-14 15:33Z

- Fresh tolerant read recovered 315 status rows from the open current-hour gzip; latest observed statuses at 15:33:25Z (1786831) and 15:33:26Z (1789161) are both `running`. No-live-match gate remains false; restart not attempted.
- Capture PID 548127 remains active, started 13 Nov 17:39:46Z. Approved source SHA is still `be437551ef871437a0a168f25ef09886dc161569c72060243393bbe8241dc8f7`; running process remains pre-edit.
- OPEN / NOT VERIFIED: restart and post-restart behavior, held until fresh source rows establish no live match.


## #339 safe-restart gate recheck — 2026-11-14 15:42Z

- Fresh tolerant read of the append-streamed 15:00Z capture shows matches 1786831 and 1789161 both `running`, with latest status updates at 15:42:09Z. The no-live-match precondition is false; restart not attempted.
- Capture PID 548127 remains active on the pre-edit process (started 13 Nov 17:39:46Z). The approved patch remains staged, not live: `live/pandascore/ll_capture.py` SHA-256 `be437551ef871437a0a168f25ef09886dc161569c720602433bbe8241dc8f7`; byte-identical backup SHA-256 `a6d7d06a962b3eeb86fac6711e6a8a47f7b6358eca7403979732245833d698ba`.
- OPEN / NOT VERIFIED: restart and post-restart proof, held until fresh source data establishes no live match.


## #339 safe-restart gate recheck — 2026-11-14 15:53Z

- The approved patch remains staged, not live; active capture PID 548127 is still running and was not stopped.
- The no-live-match gate remains false. Tolerant read of the open 15:00Z gzip recovered 643 complete rows before expected EOFError on the append-streamed file. Latest statuses: 1786831 `match_status=running` / `game_status=running` at 15:53:13Z; 1789161 `match_status=running` / `game_status=finished` at 15:52:24Z.
- Restart not attempted; no process or data was changed. The process remains on pre-edit code.
- OPEN / NOT VERIFIED: safe restart and post-restart proof, held until fresh source data establishes no match is live.


## #339 safe-restart gate recheck — 2026-11-14 16:03Z

- The approved patch remains staged, not live: `live/pandascore/ll_capture.py` SHA-256 `be437551ef871437a0a168f25ef09886dc161569c720602433bbe8241dc8f7`; backup SHA-256 `a6d7d06a962b3eeb86fac6711e6a8a47f7b6358eca7403979732245833d698ba`.
- Restart gate remains false. Freshest raw statuses show 1786831 `match_status=running` / `game_status=finished` at 16:01:56Z, 1789161 `running` / `finished` at 15:53:48Z, and 1796490 `running` / `running` at 16:03:36Z.
- Capture PID 548127 remains active on pre-edit code (started 13 Nov 17:39:46Z). Restart not attempted; no process or data changed.
- OPEN / NOT VERIFIED: restart and post-restart proof, held until fresh source data establishes no match is live.
