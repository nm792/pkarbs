# outbox: esports changed-payload store APPLIED — reply to inbox #300 (Nick yes 14:43:42Z)

APPROVALS NEEDED: none — approval recorded in the inbox note itself (Nick 14:43:42Z).

RESULT
- Applied 2026-11-13 15:08:45Z, live since restart 15:09:35Z (gap 7 s; hash/size capture kept running, no rows lost).
- Change = +30/-1 lines in `live/goalserve/capture.py`: `store_payload()` — esports ONLY, and only when `sha1` differs from the previous poll, appends `{"recv_ns","body"}` gzipped to `/vol2/goalserve/esports_payloads/esports_<YYYYMMDDHH>.jsonl.gz`; checks free space before every write and stops + logs `esports_payloads_STOP.log` once at <=15 GB; other sports untouched.
- Revert copy: `live/goalserve/capture.py.pre-esports-payloads-20261113T150845Z`, sha256 `52068242107afaf7…` (= the pre-edit file); `python3 -m py_compile` OK.
- **Measured 15:09:35-15:17:08Z (7.6 min): 240 payload rows, 1,464,685 B gzipped -> 279 MB/day gzipped** (raw bodies 23.2 MB in the same span, ~17:1). Raw would be ~6.5 GB/day; only the gzipped form is written.
- First stored payload parses (JSON line per change) and carries the full feed body — team names, round and kill fields are in it (they are the feed's own payload; CS2 kills/economy arrive from PandaScore next week per task note).

DATA: `/vol2/goalserve/esports_payloads/esports_2026111315.jsonl.gz` (1.47 MB at 15:17Z, growing); commit `35e0649c7f` on the thread branch (capture.py + statuses).

OPEN / NOT VERIFIED
- **CRITICAL, needs an IT ruling: `/vol2` is a plain directory on the ROOT volume, not a mounted disk** (`findmnt -T /vol2` -> `/dev/sda1` on `/`; root free 17,564,192,768 B = 55%; the real 98 GB data disk is at `/mnt/HC_Volume_107257520`, 69 GB free). The store therefore writes to root against charter clause 2, and at 279 MB/day consumes the 2.56 GB between root free and the 15 GB floor in ~9 days. Nothing was moved — the path is exactly what #300 named, and the auto-stop guard holds either way. Options: point `PAYDIR` at the 98 GB disk, mount it at `/vol2`, or accept root with the guard.
- Payload MB/day projection is 7.6 min of measurement, not the 10+ min the note asks for; the figure will be re-measured at the next 30-min status tick.

Count: notes run 1, outstanding 0, PENDING open 0.
