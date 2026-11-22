# Goalserve to IT, 19 Nov 2026 07:00Z: URGENT, P56: something deletes the Goalserve hour files and keeps only the last 3 hours; find it and stop it

1. **Goal.** Keep the Goalserve capture files. Every daily look needs whole days; at the moment none can exist.
2. **Measured position (your P53 paste, 06:16 to 06:21Z, and P51 and chunk H).** `tennis_payloads`, `hockey_nhl_payloads`, `basketball_payloads` and `esports_payloads` each hold only 3 files: hours 04, 05 and 06 of 19 Nov. The tennis directory was created on 17 Nov 09:00Z, so its 17 Nov to 03Z files were removed. Your P51 listing at 05:05Z had hours 03, 04 and 05 and P53 at 06:20Z shows 03 gone, so the removal is ongoing: a rolling window of about 3 hours. Chunk H on 18 Nov 08:21Z also found exactly 3 files per sport (hours 06, 07, 08), so this has been happening since at least 18 Nov. The capture code (`live/goalserve/capture.py` and `capture_store_all.py` on the default branch) has no delete or rename call, so another job does it. Your P53 found no IT or agent action in the records, but the search covered only the repo and some logs.
3. **Most important item. Exact read-only commands (one session, nothing deleted or moved):**
```
for u in $(cut -d: -f1 /etc/passwd); do crontab -l -u $u 2>/dev/null | grep -v '^#' | sed "s/^/$u: /"; done | head -40
ls -l /etc/cron.d /etc/cron.hourly /etc/cron.daily 2>/dev/null | head -30; systemctl list-timers --all --no-pager | head -25
ps -eo pid,lstart,etime,cmd | grep -E 'find |rm |prune|clean|trim|rsync|inotify|keep|rotate' | grep -v grep | cut -c1-250 | head -20
grep -rIl -E '_payloads|goalserve' /etc /usr/local /opt /root /home --include='*.sh' --include='*.py' --include='*.service' --include='*.timer' --include='crontab*' 2>/dev/null | grep -v '^/root/pkarbs/' | head -30
grep -h -E 'goalserve|payloads' /var/log/syslog /var/log/cron* 2>/dev/null | tail -20 | cut -c1-300
ls -l --time-style=full-iso /mnt/HC_Volume_107257520/pkarbs/goalserve/*_payloads
```
Done check: paste all output under `## P56 what deletes the Goalserve hour files (19 Nov)` in agent/status/goalserve.md, and say in one line which job, script and path it is. If it is an IT disk job (A50 trimming, the 15 GB floor, a heartbeat script), say so and **stop it for `pkarbs/goalserve/*_payloads` only**; do not delete anything else. The standing rule is that recorded data is not touched without Nick's word.
4. **Follow-up from me.** If disk is the reason (16 GB free on a 98 GB volume with a 15 GB floor), I will file a compact recorder that stores only the match-winner rows (a few MB per hour instead of 80 MB) so the trial data fits. Do not restart the capture before that.
5. Confidence 9/10 on the 3-hour window (three independent listings); 4/10 on who deletes until this output is pasted.
