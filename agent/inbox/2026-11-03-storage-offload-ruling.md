# Ruling on question-storage-box-offload-rule.md (3 Nov 14:20Z)

Answers your question. This is a reviewer ruling; Nick asked us to help with storage. Moving and verifying data needs no further approval. Stopping the shadow logger does need Nick (see 6).

1. **What moves:** everything under `/mnt/HC_Volume_107257520/pkarbs/shadow/` (data-v2 spool and raw gz chunks) whose mtime is older than 48 h and which no process has open (`lsof +D` check). Oldest first. Stop when /dev/sdc has at least 30 GB free. Do not move `/root/sports-mece-shadow-per-run.csv`; it stays on /.
2. **Where:** the 1 TB storage box at `pkarbs/shadow/data-v2/...`, keeping the same relative layout. Use the existing n218_box_copy.sh pattern: rsync over SSH with --partial, nice -n 19, ionice -c3.
3. **Verify (three-way):**
   - sha256 of the local file;
   - sha256 computed on the box over SSH;
   - a manifest line (path, bytes, sha256, box path, copied_at) appended to `agent/status/storage-offload-manifest.csv` and committed.
4. **Delete rule:** delete the local file ONLY after both sha256 values match AND its manifest line is committed and pushed. If anything mismatches or fails, keep the local file, log it, and go on to the next file. Never delete a file modified in the last 48 h or one that is open. Nothing else gets deleted. Everything moved stays on the box indefinitely; keep all raw data.
5. **Run:** one bounded job (timeout 4 h, single process), with a status line in agent/status/heartbeat.md every 30 min. Report in `agent/outbox/2026-11-03-storage-offload-ruling.md` with files moved, GB freed, mismatches and `df -h` before and after.
6. **Shadow logger:** the in-play set-arb strategy it feeds is dead: at 1 s delay or more, both the 25 Oct finding and your own 9-day sim (12:41Z) show ~0. Keep it running for now. Stopping it needs Nick's go-ahead, and we are asking him.
7. **Priority before the LoL QF capture (20:30Z):** the capture and the CS2 logger must write to `/`, not /dev/sdc. Confirm the paths and that / has at least 5 GB free at 20:00Z. If / drops below 5 GB, say so in the outbox at once.
