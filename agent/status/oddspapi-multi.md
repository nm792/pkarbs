# status: oddspapi-multi (TASK-oddspapi-multi-2026-11-05)
state: DONE (data committed 2026-11-05T06:40Z)
owner ruling: agent/outbox/question-2026-11-05-tennis-oddspapi-disk-gate.md (05:25Z) — gate root >= 6 GB free.
run: pull_hist_multi.py (pid 2705158), started 2026-11-05T05:32:20Z, finished 06:10:26Z.
result: log ev=done, hist_ok 408/429 (>=100 PASS), hist/ has all 8 sport prefixes (>=5 PASS). PASS.
disk after: / 6.8 GB free (06:34Z).
commit: per-sport tarballs to rn1/scores/oddspapi/multi-2026-11-05/ (single 172MB tar exceeds GitHub 100MB limit, split into 8 sub-100MB sport files), commit 80004ef7.
cleanup: /root/oddspapi/multi-2026-11-05 deleted after commit. Key never committed.
last heartbeat: 2026-11-05T06:40Z UTC
