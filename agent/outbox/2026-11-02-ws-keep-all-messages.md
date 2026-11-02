# ws-keep-all-messages — APPLIED (approved 2 Nov)

## APPROVALS NEEDED
- ws-keep-all-messages: APPROVED by Nick at ~14:0xZ 2 Nov. Code edit + process restart. Applied.

## RESULT
- /root/cs2logger/logger.js line 24: dropped the `if (g.leagueAbbreviation !== 'cs2') return;` filter.
  Now EVERY sports-WS frame is appended to cs2_frames.jsonl (incl. NPL cricket, Spanish 2a, all leagues).
  Guard-only change; the change/score line stays as-is. node --check PASS.
- Logger relaunched as a detached transient unit (the previous cs2-logger.scope was a systemd-run
  transient, not a restartable service; it stopped cleanly): `cs2-logger.service`
  `systemd-run --unit=cs2-logger -p MemoryMax=512M -p MemorySwapMax=0 timeout 43200 env NODE_PATH=... HOURS=12 OUT=/root/cs2logger/out node /root/cs2logger/logger.js`.
- VERIFIED: unit active, pid 3442185; the latest captured frame is `leagueAbbreviation:"es2"`
  (CD Tenerife v FC Andorra, InProgress, score 2-0, 14:10Z) — a non-cs2 league that the old guard
  would have dropped. Proof the keep-all filter works.
- Repo copy agent/tasks/cs2-ws-logger/logger.js mirrored to match the running file; pushed (74242b4).

## DATA
- Live logger: /root/cs2logger/logger.js (edited), output /root/cs2logger/out/cs2_frames.jsonl.
- Unit: cs2-logger.service active, MemoryMax=512M, timeout 43200.

## OPEN / NOT VERIFIED
- The watchdog.sh still restarts "node logger.js" under the edited file on failure (same file), so keep-all persistence holds across watchdog restarts. The watchdog reads `run.flag`; it was running as written.
- CS2-specific processing (score strings map to hltv event ids) unchanged — the CS2 stream is a subset of all-sports capture; the CS2 reports continue to use the CS2 rows only.

## Count
notes run 1, outstanding 0, "waiting for Nick" cleared.

## Context
Note 2026-11-02-ws-keep-all-messages. Reason: NPL cricket 3 Nov and other leagues need persisting
for the sports-MECE work. Live capture continues on the ORIGINAL CS2 transform (no data loss); the
change only widens what is PERSISTED (raw frames), not what the CS2 pipeline consumes (still CS2-only).
