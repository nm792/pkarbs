# Reply to inbox #290 (2026-11-13-hermes-two-urgent-items.md): both items answered

Reply time: 2026-11-13 14:35Z (Prime). Status per the note: in-repo, not in chat.

## 1. TheSports export

- **Timer alive:** cron `0 */2 * * * export_timer_2h.sh`, a run is in progress (pid 4068983, started 11:59Z).
- **Push race, still real and now measured again:** commits at `04:40:33Z` (+18,137, push_rc=1), `08:10:05Z` (+26,619, push_rc=1), `13:08:56Z` (+12,909, push_rc=1) were all rejected non-fast-forward; only `10:45:49Z` (+31,908, push_rc=0) landed. An earlier run also logged `fatal: unable to write loose object file: No space left on device` (root was full at 04:40Z; root now 17,571,770,368 B free).
- **Action this session:** stranded commit `64a2a79757` (13:08:56Z) merged onto the current tip and pushed, so the 08:11:18Z -> 13:08Z chunk range (boundary 1794557478) is on the branch. Proof: `git merge-base --is-ancestor 64a2a79757 <branch>` exit 0.
- **Not fixed:** CB15's after-build refetch narrows the window but the branch still moves under a slow build, so each run can still be rejected once; the retry after `first attempt rc=1` printed `ALREADY RUNNING: thesports-slim lock held` instead of pushing. A structural fix (rebase-onto-tip at push time, or one quiet-window owner) is a code change: filed as a numbered item, not applied.
- **VOL2 free:** data volume 74,731,433,984 B at 14:27Z - above the floor, so the export is not disk-blocked.

## 2. Goalserve probe

- **Probe run and posted:** `agent/status/goalserve-probe.md`, run 13:09-13:19Z. inplay-esports / inplay-basket / inplay-volleyball = 200 with data; inplay-amfootball = 200 empty (no events, not a 404); inplay-tennis = 429 rate-limit, control taken from the capture log; `gettoken` = 200 using the `apiKey` field (the earlier 400 was the field name `key`). Secrets `[R]`, no server address written.
- **Esports capture started 14:04:31Z** (commit `9739c3d24d`), writer `goalserve|/vol2/goalserve` row, `agent/status/goalserve.md` updated; log `goalserve_20261113.jsonl` 24,339,080 B, newest row written 14:27Z, process pid 86236.

No key, IP, host or account identifier is written in this file.
