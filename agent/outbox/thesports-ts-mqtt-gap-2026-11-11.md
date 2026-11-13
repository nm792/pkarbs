# reply: ts_mqtt / books_mid export gap (11 Nov 2026, 09:45Z; CORRECTED 11:10Z)

Priority export (inbox `thesports-ts-mqtt-gap-2026-11-11`). State as of this pass.

## Why the timer runs after 00:22Z did not push — measured
- **Push race (primary).** Every 2h timer commit since 00:22Z was built and committed locally but its push was REJECTED `non-fast-forward` (see /var/log/thesports_export_timer.log): 02:25Z +7205, 02:55Z +8738, 05:16Z +14431, 06:52Z +18786, 09:59Z +25101 (`b091e49b`) files, all `push_rc=1 ... rejected (non-fast-forward)` because the 15-min dispatch (heartbeat + replies) keeps advancing `claude/project-thread-vg2ckg` while the ~1-2h slim build runs. The retry-on-fresh-tip also loses the race (branch never quiesces long enough; the retry rebuilds for ~1h and origin moves again).
- **Guard syntax error (secondary, transient).** An 08:00Z run aborted at line 78 of `live/thesports/export_timer_2h.sh` (`syntax error near ... -$( printf ... )`), so two timer windows were lost to a broken shrink-guard echo. The file on disk now passes `bash -n` and is byte-identical to origin (15407a49 guard), so this is corrected; the race remains.

## Follow-up verify (11:10Z) — data NOT yet landed on origin
Newest committed ts_mqtt chunk on `origin/claude/project-thread-vg2ckg` is STILL the 00:22Z one (**1794355250**, 00:22:50Z) in `rn1/scores/thesports/final-topics-32295b-slim/ts_mqtt/`. The worker's last build (09:59Z, 25101 files) was again push-rejected non-fast-forward; it is retrying. No slim export has landed since 00:22Z.

## Reason for the stalled timer (confirmed)
The new >5% shrink guard (15407a49) did NOT refuse the whole export — no `SKIP` lines in the log; the blocker is the push race plus one transient guard syntax error (now fixed on disk). The durable fix is a code change to `export_timer_2h.sh` (build the slim commit, then rebase/merge-commit onto the CURRENT origin tip at push time, or push in the quietest window) — **now logged as CHANGE-BATCH #15** (tt-review dialogue). Row 13 stays OPEN until the fix is applied and the data lands.

## Data already captured (not lost)
Live source ts_mqtt.jsonl (4.9 GB) and books.jsonl (6.4 GB) under `/mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b/` are complete and growing (newest 09:44Z+); nothing was deleted. The 8 h of tennis/Dota messages (00:22Z-now) are recorded on the volume, absent only from the repo slim copy.

## UPDATE (11:10Z 11 Nov) — data LANDED on origin
A manual merge commit (**6cf032317a**) was built by overlaying the 09:59Z slim build (`b091e49b`, ts_mqtt 00:22Z→10:00Z, 218,056 ts_mqtt files + books_mid) onto the current origin tip and pushed fast-forward. Verified on `origin/claude/project-thread-vg2ckg`: newest ts_mqtt chunk **1794384000000** (10:00:00Z) and newest books_mid chunk **1794384000000** — the 8 h of tennis/Dota/other messages (00:22Z→10:00Z) are now on the slim repo branch. The durable fix (rebase/merge at push time) is still CHANGE-BATCH #15, approval-gated under 409 (11-08..15); OPEN row 13 stays open only for that code fix and any newer 10Z+ chunks the timer still fails to push.
