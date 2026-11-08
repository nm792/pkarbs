# Outbox: rugby windows D and C preflight (8 Nov 2026)

From: server-member (Hermes), 04:05Z. Answer to `agent/inbox/rugby-d-c-preflight-2026-11-08.md`. Read-only — no code/path change, no restart. Re-measured this run.

## 1. Launch schedule for D (13:45Z) and C (19:50Z)
**NO auto-launch exists.** `crontab -l` has no rugby line, `atq` empty, no systemd timer matches `rugby`. Launch is manual: I start capture.py at the window's start time per TASK-rugby-top14-capture (D 13:45Z, C 19:50Z), the same way AB was launched manually 7 Nov 13:00Z. Nothing currently scheduled will fire D or C by itself.

## 2. Single-instance flock guard (#187, ce3166ab)
**NO — the working-tree copy the launch would run does NOT carry the guard.** `agent/tasks/rugby-top14-capture.py` (sha256 2742f3df…, both the local checkout and the newest-thread blob e14bc2ac) has zero `flock`/`fcntl` lines. The #187 lock (commit ce3166ab, `fcntl.flock LOCK_EX|LOCK_NB`) exists only on branches `project-thread-vg2ckg` / `pf5upe` / `sk8ngs` — it is NOT an ancestor of the newest thread `tgoj9t`. The AB run hit exactly this: 5 concurrent processes wrote interleaved rows to the same AB_*.jsonl (approved consolidation pending). **Recommendation: launch D/C from a copy carrying the ce3166ab lock** (or confirm the single-writer precondition by `pgrep` before each start). This is a code-selection decision — flagging, not changing.

## 3. Write target and disk headroom
**ROOT resolves OFF the root disk — no charter breach.** `readlink -f /root/pkarbs/rugby` = `/mnt/HC_Volume_107247271/git/pkarbs/rugby` (findmnt TARGET `/mnt/HC_Volume_107247271`, /dev/sdb). Freed space: volume `/dev/sdb` **20G avail** (49G, 58%), root `/dev/sda1` 19G avail (38G, 47%). AB's Rugbyrama leftovers sit on the volume: `AB_rugbyrama.jsonl` 1.32 GB (1,324,639,767 B, 7 Nov 18:00), `AB_espn.jsonl` 39.6 MB. Nothing on the root disk. D/C need ~6 tokens / a fraction of a GB — ample headroom. PASS on disk.

## 4. CLOB price-stream state and D plan
**The stream is NOT fixed — D must use the REST 5 s fallback.** The 301 s probe (18:33Z) and the AB run both show the WS opens (`CLOB open`) but NO stream file — AB captured only `AB_clob_rest.jsonl` (9,756 rows, `mode:"5s-poll"`), no `AB_clob.jsonl` stream rows. Same on the re-probe run presented in this preflight. So D and C will run on REST book polls every 5 s (tokens: the 6 D / 6 C `clobTokenIds` from the window config). Fallback is recorded, not a task failure, and lag figures will be labeled "5 s poll resolution" — not "stream". Score side: sports WS showed no `rutopft` rugby messages in the windows; ESPN 270559 is the primary score clock for Top 14 (as in AB).

## Summary
D/C are runnable on disk and score-side, but (a) no auto-launch is scheduled — manual start, and (b) the flock guard is absent from the launch copy (duplicate-writer risk already observed in AB); recommend launching from the ce3166ab-guarded copy. CLOB prices = REST 5 s fallback for both windows.

Count: notes run 1, outstanding 0, PENDING open 0. Waiting on Nick: none (read-only preflight).
