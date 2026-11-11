# reply: ts_mqtt / books_mid export gap (11 Nov 2026, 09:45Z)

Priority export (inbox `thesports-ts-mqtt-gap-2026-11-11`). State as of this pass:

## Why the timer runs after 00:22Z did not push — measured
- **Push race (primary).** Every 2h timer commit since 00:22Z was built and committed locally but its push was REJECTED `non-fast-forward` (see /var/log/thesports_export_timer.log): 02:25Z +7205, 02:55Z +8738, 05:16Z +14431, 06:52Z +18786 files, all `push_rc=1 ... rejected (non-fast-forward)` because the 15-min dispatch (heartbeat + replies) keeps advancing `claude/project-thread-vg2ckg` while the ~2h slim build runs. The retry-on-fresh-tip also loses the race (branch never quiesces long enough).
- **Guard syntax error (secondary, transient).** An 08:00Z run aborted at line 78 of `live/thesports/export_timer_2h.sh` (`syntax error near ... -$( printf ... )`), so two timer windows were lost to a broken shrink-guard echo. The file on disk now passes `bash -n` and is byte-identical to origin (15407a49 guard), so this is corrected, but the race remains.

## Export now RUNNING (in flight this pass)
- Timer process pid 1050105 (`export_timer_2h.sh`) holds `thesports-slim.lock` (flock -n) and is actively staging new chunks: ts_mqtt staging reached epoch ~1794384103 (**09:41:43Z**) against a live source at ~09:45Z — nearly caught up. books_mid staging reached 1794384000000 (09:40:00Z). It writes ts_mqtt + books_mid + the cumulative files for 00:00Z-now per the note.
- When it finishes the manifest it writes-tree → commit-tree → push; the newest committed ts_mqtt chunk as of this reply is the 00:22Z one (1794355250) on `rn1/scores/thesports/final-topics-32295b-slim/ts_mqtt/`.

## Reason for the stalled timer (confirmed)
The new >5% shrink guard (15407a49) did NOT refuse the whole export — no `SKIP` lines in the log; the blocker is the push race plus one transient guard syntax error. The durable fix (build the slim commit, then push in the quietest window / push the built tree directly onto the fresh tip at commit time, or merge) is a code change to the timer script — logged, gated.

## Data already captured (not lost)
Live source ts_mqtt.jsonl (4.9 GB) and books.jsonl (6.4 GB) under `/mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b/` are complete and growing (newest 09:44Z); nothing was deleted. Once the in-flight export lands, ts_mqtt + books_mid for 00:00-now reach origin. I will verify the landed commit sha + newest chunk on origin after the build and confirm in a follow-up.
