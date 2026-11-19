# IT TASK (URGENT, deploy only): Elon 48h listing book recorder, persistent, next listing Sat 21 Nov 17:07:01Z

From the pipeline thread. Read-only: never places orders, no keys. Deploy committed code, run the stated commands, do not edit code. Nick does not SSH; you run everything and paste output.
Why: Nick wants the live book at each new Elon bracket listing captured to the second. The first listing today (17:07:01Z) was captured 5 min 59 s late because a recorder process I ran in a throwaway container died. Pre-registered rule: pipeline/forward/RULE-elon-listing.md (commit 56fdf695aa, Amendment 1 in db0de45afd).

## Steps
1. `cd /mnt/HC_Volume_107257520/pkarbs && git fetch origin claude/project-thread-o5rbz8 && git checkout FETCH_HEAD -- pipeline it` (do NOT commit from /root/pkarbs). Print `git rev-parse HEAD`-equivalent: the commit in the merge note, and `sha256sum pipeline/forward/elon_listing.py`.
2. `python3 -m pytest -q pipeline/tests/test_elon_listing.py` and paste the last line (expect `... passed`).
3. `mkdir -p /mnt/HC_Volume_107257520/elon-listing && cp pipeline/forward/data/elon_hourly.json /mnt/HC_Volume_107257520/elon-listing/hourly.json` (seed counts to 19 Nov 06:00Z).
4. Counts refresh: `python3 pipeline/forward/refresh_elon_hourly.py /mnt/HC_Volume_107257520/elon-listing/hourly.json` (exit 0 PASS = xtracker reachable from the server; exit 3 = host blocked, then tell the thread: it will commit a fresh `pipeline/forward/data/elon_hourly.json` daily and you copy it). If exit 0, add cron: `0 7 * * * cd /mnt/HC_Volume_107257520/pkarbs && python3 pipeline/forward/refresh_elon_hourly.py /mnt/HC_Volume_107257520/elon-listing/hourly.json >> /mnt/HC_Volume_107257520/elon-listing/refresh.log 2>&1`.
5. Install as a PERSISTENT service (not systemd-run): `cp it/units/elon-listing.service /etc/systemd/system/ && systemctl daemon-reload && systemctl enable --now elon-listing.service`. Restart=always is in the unit.
6. `bash it/elon_listing_preflight.sh` and paste the whole output (every FAIL fixed within 15 min or named). Then `bash it/elon_listing_live_read.sh` (before a listing it prints DOWN-or-between-listings for growth: that is normal; the pid line must show a number).
7. Disk: capture is about 40 MB per listing for the first 6 hours; keep the 15 GB root floor.

## Schedule (details and times: it/SCHEDULE-elon-listing-2026-11-19.md)
Listings are every Mon, Thu and Sat at 17:07:01Z (16:07:01Z in summer time). Next: Sat 21 Nov. At least 30 minutes before each listing (16:37Z) run `it/elon_listing_preflight.sh` and paste it; at 17:02Z run `it/elon_listing_live_read.sh` and paste it. A listing without a pasted T-30 preflight is a missed window.

## Report in agent/outbox
`systemctl is-enabled`, `systemctl is-active`, pid, the sha256, the preflight output, and after each listing the first/last snapshot times from `<out>/<event_id>/books.jsonl` (expect about 1 line per second for 30 minutes, then every 5 s) and the number of `error` lines in `journalctl -u elon-listing.service` (expect 0).
