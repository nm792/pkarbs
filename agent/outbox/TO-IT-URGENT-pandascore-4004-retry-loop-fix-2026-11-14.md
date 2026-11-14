# PK arbs #339 — PandaScore 4004 retry-loop fix

- IT approved the three specified edits in `agent/inbox/IT-REPLY-4004-fix-2026-11-14.md`. The byte-identical pre-edit backup SHA-256 is `a6d7d06a962b3eeb86fac6711e6a8a47f7b6358eca7403979732245833d698ba`; the staged live-file SHA-256 is `be437551ef871437a0a168f25ef09886dc161569c72060243393bbe8241dc8f7`; `py_compile` passes.
- Restart remains held under the approval's no-live-match condition. At 14:17:46Z, the latest raw status rows showed seven matches running (1762448, 1785760, 1786830, 1793319, 1796496, 1803636, 1807005). The existing process remains PID 548127, started 13 Nov 17:39:46Z, before the edit; no restart was attempted.
- The live output file continued growing; the latest observed row was 14:17:46Z.
- **OPEN / NOT VERIFIED:** wait until no match is live, then restart and verify the new process and post-restart 4004 behavior. No further approval is needed; the safety precondition is currently false.
