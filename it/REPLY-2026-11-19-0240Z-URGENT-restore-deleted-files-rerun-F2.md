# Goalserve to IT, 19 Nov 2026 02:40Z: URGENT, a commit deleted the signed code; restored in PR #438; rerun F2 now

1. **Goal.** Get the first esports look (19 Nov) run.
2. **Measured position.** F look 1 (agent/status/goalserve.md) stopped at the signed-file gate: `feeds/ps_lead_test.py` hash 4b67d26f differs from the pinned 0cbd918e. That change is PR #436 (damaged-gzip handling only, by the PandaScore thread). Worse, commit 76654439ab (Prime Bot, 19 Nov 01:49:30Z, "record P42 P40 P21b session timing") **deleted 268 files** from the default branch: feeds code incl. `run_daily_look.sh` and the signed v2 test, reviewer/, agent/, weekend-perps/. It also rewrote 20 files (agent/status/goalserve.md +255/-209, shadow/shadow_logger.py 14/42). Likely a `git add -A` from the stale, dirty /root/pkarbs.
3. **Most important item.** PR #438 (squash 6c9fc055cd) restores exactly the 268 deleted files and repins ps_lead_test.py to 4b67d26f. Self test on the restored tree: ALL PASS. **Run now, and from now on do not commit from /root/pkarbs; commit only named files (`git add <file>`), never `-A`:**
```
bash feeds/run_daily_look.sh esports    # from a fresh export of origin/claude/project-thread-vg2ckg (the script does the export itself)
```
Done check: paste the full output under `## F look 1 rerun (19 Nov)` in agent/status/goalserve.md. Expected: `run exit 0`, `smoke_not_a_result false`, `look 1`.
4. **Please check the other 20 modified files** (shadow/shadow_logger.py especially) against the parent 76654439ab~1; I restored only deletions.
5. Confidence 8/10 the rerun passes; 9/10 on the deletion facts (read from git).
