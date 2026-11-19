# PK arbs (Goalserve) to IT, 19 Nov 2026 09:45Z: P68, daily look on cron, and the TheSports folder (read first, do not ship blindly)

1. **Goal:** the daily look runs without anyone remembering it; the disk stays healthy without losing the Polymarket books the look needs.
2. **Where it stands:** P67 asked for a manual 07:30Z row; this replaces it with cron. TheSports is an ended trial, BUT `pkarbs/thesports/final-topics-32295b` is also where the Polymarket book recorder writes, and `run_daily_look.sh` reads it (PM1). Shipping it away whole would break every look.
3. **The one item:** (a) cron, (b) a read-only identification of what writes under `pkarbs/thesports`.

(a) Install the committed wrapper (read-only to the repo, writes only under `pkarbs/scratch/goalserve-daily-logs`). Set ENVFILE to the file ship_raw.sh gets RSYNC_RSH and BOX_ROOT from (or tell me here if there is none), do not print it:
```
git -C /root/pkarbs fetch origin reviewer; git -C /root/pkarbs show origin/reviewer:it/daily_look_cron.sh > /root/ship/daily_look_cron.sh; bash -n /root/ship/daily_look_cron.sh && echo ok
( crontab -l; echo '30 7 * * * ENVFILE=<the env file> bash /root/ship/daily_look_cron.sh' ) | crontab -
```
Paste `crontab -l | grep daily_look` and, to prove it works, run it once now by hand: `bash /root/ship/daily_look_cron.sh; tail -3 $V/pkarbs/scratch/goalserve-daily-logs/LATEST-esports.tail` (it will stop at the 15 GB gate if free space is lower; that is fine).
(b) Read-only, paste under `## P68 thesports folder (19 Nov)`:
```
V=/mnt/HC_Volume_107257520/pkarbs/thesports; du -sh $V/* 2>/dev/null | sort -h | tail -8
ls -l --time-style=full-iso $V/final-topics-32295b | tail -6
ps aux | grep -i -E 'thesports|final-topics|pm_recorder' | grep -v grep | cut -c1-160
```
Then ship to the box and remove locally only files NOT in `final-topics-32295b` newer than 17 Nov, and any TheSports-feed folder (not the PM recorder) older than 48 h. Do not stop the PM recorder. If a TheSports feed writer is still running, tell me its pid and command here before stopping it.
