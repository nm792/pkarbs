
## #339 safe-restart gate recheck — 2026-11-14 15:13Z

- Approved patch remains staged only: `live/pandascore/ll_capture.py` SHA-256 `be437551ef871437a0a168f25ef09886dc161569c72060243393bbe8241dc8f7`; byte-identical backup `live/pandascore/ll_capture.py.pre-339-20261114T135600Z`, SHA-256 `a6d7d06a962b3eeb86fac6711e6a8a47f7b6358eca7403979732245833d698ba`. Compile passed in prior verification.
- No-live-match gate is not met. Tolerant read of the append-streamed current-hour file recovered two latest status rows: match 1786831 `running` at 15:12:55Z and match 1789161 `not_started` at 15:12:45Z. Earlier current-hour rows also include live matches. Restart not attempted.
- Capture process PID 548127 remains on the pre-edit version (started 13 Nov 17:39:46Z). The 4004 retry loop for match 1789154 remains visible in the event log; the approved fix is not live.
- OPEN / NOT VERIFIED: safe restart and post-restart behavior. Recheck only when the source advances; restart only after the approved no-live-match condition is established.
