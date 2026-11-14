# PK arbs #339 — PandaScore 4004 retry-loop fix

- IT approved the exact three edits in `agent/inbox/IT-REPLY-4004-fix-2026-11-14.md`; no extra approval is pending.
- Backup: `live/pandascore/ll_capture.py.pre-339-20261114T135600Z` (SHA-256 `a6d7d06a962b3eeb86fac6711e6a8a47f7b6358eca7403979732245833d698ba`). Edited file SHA-256: `be437551ef871437a0a168f25ef09886dc161569c72060243393bbe8241dc8f7`; `py_compile` passed.
- The edit stops each 4004 task, logs per-match 4004 counts, adds the 300-second post-task retry cooldown, and waits until `opens_at`.
- Restart not run: raw rows at 13:56:28Z showed three matches (`1796496`, `1793319`, `1803636`) still running. PID 548127 remains on the pre-edit code; the change is committed but not live.
- OPEN / NOT VERIFIED: safe restart and post-restart proof.
