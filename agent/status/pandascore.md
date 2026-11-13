# status: PandaScore low-latency feed (v2) - BLOCKED, token missing

Updated: 2026-11-13 14:35Z UTC (first status, ahead of the 14:45Z deadline in inbox `pandascore-live-now-2026-11-13.md`).

- **1. Token:** `token missing`. `/etc/pkarbs/pandascore.env` does not exist (checked 14:3xZ, `ls` returns "No such file or directory"). Nothing was asked of Nick from this repo; the coordinator carries that once, per the note. If the token arrives it goes to `/etc/pkarbs/pandascore.env` (mode 600, never printed, logged or committed).
- **2. Client build:** not started - the v2 task's client needs `PANDASCORE_TOKEN` to open `/matches/{id}/low_latency_feed`; with no token every socket would fail, so no client was written against an unreachable endpoint.
- **3. Class-4 item filed:** a new collector start is class 4 under charter clause 5 unless the note carries a measured 1-hour MB/day, a spool path on the data volume, a box folder, retention, a writers.conf row with a pause hook, headroom and a revert. Numbered item recorded in the governance approvals file with the exact change and revert; it waits for the daily batch.
- **4. Next status:** every 30 minutes while blocked (15:05Z, 15:35Z, ...), in this same file.
- **Capture:** not running. Capture start and verification remain due 2026-11-16 12:00Z (BLAST Slam Dota 17 Nov).

Blocked-on: PANDASCORE_TOKEN in `/etc/pkarbs/pandascore.env`.
