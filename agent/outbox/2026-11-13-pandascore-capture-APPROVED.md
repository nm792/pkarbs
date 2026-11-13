# outbox: PandaScore low-latency capture STARTED — reply to inbox #301 (Nick yes 14:44:29Z)

APPROVALS NEEDED: none — approval recorded in the inbox note (Nick 14:44:29Z).

RESULT
- Token installed (not printed anywhere): present in `/root/API_KEYS/pandascore/.env`, mode 600, `PANDASCORE_ACCESS_TOKEN` (51 bytes, supplied 13 Nov). **`/etc/pkarbs/pandascore.env` could not be written** — the terminal refuses `/etc` writes in unattended runs (consent gate, no user present), so the client checks `/etc` first and falls back to the API_KEYS file; one interactive run can create the `/etc` copy and the client picks it up on next restart. Token grep over logs/status/data = 0 hits; never logged in a URL.
- Client built and started: `live/pandascore/ll_capture.py` (214 lines, `py_compile` OK), tmux `pandascore`, pid 212720, start **15:12:29Z** (first capture of the day, per the task deadline).
- Discovery every 60 s (Bearer header) on the low-latency feed list; Dota 2 + CS2 only, LoL skipped; one socket per match at/after `opens_at`; close codes per task (1000 stop, 4004 re-check discovery, 4001/4003/4029 log-and-stop-no-retry, 1xxx/no-code backoff 1-30 s); silence >300 s logged, socket never killed on a timer; every message logged with recv_ns, sha1, updated_at, available_fields and the raw payload.
- **10 sockets connected at 15:12:29Z** (6 CS2, 4 Dota 2); **45 raw rows by 15:13Z, first row `kind=hello`** — capture verified running today, 3 days ahead of the 16 Nov 12:00Z bar.
- Output: `/vol2/pandascore/raw/pandascore_<YYYYMMDDHH>.jsonl.gz` (gzip, flush per row, closed at UTC hour rollover) + `/vol2/pandascore/events.jsonl.gz`. Free at start 17,564,192,768 B (>15 GB floor); auto-stop guard in code.
- Status every 30 min in `agent/status/pandascore.md` (next 15:47Z, 16:17Z).

DATA: commit `35e0649c7f` on the thread branch (`live/pandascore/ll_capture.py`, statuses); `/vol2/pandascore/raw/pandascore_2026111315.jsonl.gz`.

OPEN / NOT VERIFIED
- First-hour MB/day figure due ~16:12Z (not yet measured).
- **Same CRITICAL as the goalserve reply: `/vol2` resolves to the ROOT volume** (`findmnt -T /vol2` -> `/dev/sda1` on `/`), not a mounted disk; the 98 GB data disk is at `/mnt/HC_Volume_107257520`. The task names `/vol2`, so nothing was moved; IT to rule on redirecting or mounting.
- No box/writers.conf row yet (charter clause 5: measured MB/day first, then the row + pause hook).

Count: notes run 1, outstanding 0, PENDING open 0.
