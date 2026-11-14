# PK arbs #339 — PandaScore 4004 retry-loop fix

- IT's approval for the three specified edits is on origin in `agent/inbox/IT-REPLY-4004-fix-2026-11-14.md`.
- Backup SHA-256: `a6d7d06a962b3eeb86fac6711e6a8a47f7b6358eca7403979732245833d698ba`; live edited file SHA-256: `be437551ef871437a0a168f25ef09886dc161569c72060243393bbe8241dc8f7`. `py_compile` passed.
- Safe restart remains held. Raw status at 14:07:58Z showed matches 1793319, 1803636 and 1807005 running; the 14:08Z sample still showed all three active. PID 548127 predates the edit, so the fix is staged but not live. Capture output continued growing.
- OPEN / NOT VERIFIED: restart only after no match is live; then verify the new process and 4004 retry behavior. No restart was attempted and no additional approval is pending.
