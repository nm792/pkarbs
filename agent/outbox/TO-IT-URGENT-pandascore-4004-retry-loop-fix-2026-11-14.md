# PH #339 — safe-restart gate recheck (2026-11-14 15:23Z)

- The approved patch is staged, not live: `live/pandascore/ll_capture.py` SHA-256 `be437551ef871437a0a168f25ef09886dc161569c72060243393bbe8241dc8f7`; byte-identical backup SHA-256 `a6d7d06a962b3eeb86fac6711e6a8a47f7b6358eca7403979732245833d698ba`. No code changed.
- The no-live-match restart condition is not met. Tolerant reading of the still-open `pandascore_2026111415.jsonl.gz` found latest status rows at 15:23:35Z: match 1786831 `running`; match 1789161 `running`.
- Restart not attempted. Capture PID 548127 remains the pre-edit process, started 13 Nov 17:39:46Z. Live event rows still show match 1789154 code-4004 closes approximately every 10 seconds through 15:23Z.
- OPEN / NOT VERIFIED: restart and post-restart behavior; the no-live-match precondition must first be established from fresh source rows.
