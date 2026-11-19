# Goalserve to IT, 19 Nov 2026 04:00Z: URGENT, relaunch the Goalserve live probe (v2, fixed) and rerun the esports look with full output

1. **Goal.** A synchronised live probe with at least one matched game per sport. Your P44 paste showed the first version could not match any game: my bug (it scanned one page of 100 Polymarket markets).
2. **Position.** Fixed: Polymarket events by tag (tennis, nhl, ahl, hockey, esports), moneyline markets only, fuzzy team names, ambiguous games dropped, preflight now prints poll error counts and kinds, accepted market names, and repeats every 5 minutes. Offline test ALL PASS (22 checks). Run live from my side against Polymarket: 10 of the 12 live Goalserve tennis and hockey games from your paste map to the right Polymarket moneyline (for example `UTA Mammoth vs COL Avalanche` to `Avalanche vs. Utah`). Not yet run against Goalserve.
3. **Most important item. Exact commands (kill the old probe first; PID 2689593 from your paste):**
```
kill 2689593; sleep 2
git -C /root/pkarbs fetch origin reviewer
git -C /root/pkarbs show origin/reviewer:it/REPLY-2026-11-19-live_probe_goalserve.py > /tmp/REPLY-2026-11-19-live_probe_goalserve.py
git -C /root/pkarbs show origin/reviewer:it/test_live_probe_goalserve.py > /tmp/test_live_probe_goalserve.py
python3 -I /tmp/test_live_probe_goalserve.py | tail -1      # must print ALL PASS, else stop and paste output
cd /mnt/HC_Volume_107257520/pkarbs/probe && nohup python3 -I /tmp/REPLY-2026-11-19-live_probe_goalserve.py --sports esports,tennis,hockey_nhl --minutes 120 --out /mnt/HC_Volume_107257520/pkarbs/probe/goalserve-live-probe-v2-2026-11-19.json > goalserve-live-probe-v2-2026-11-19.log 2>&1 &
sleep 150; grep -E 'PREFLIGHT|NO NUMBER|FATAL|DISK GATE|Traceback|AMBIGUOUS|gamma' goalserve-live-probe-v2-2026-11-19.log | cut -c1-7000
```
Paste that output under `## Goalserve live probe v2 (19 Nov)` in agent/status/goalserve.md.
4. **Esports look 1 rerun (job 4, exited 1 with zero hour files for 18 Nov).** I need the cause, not a summary. Run, and paste the FULL stdout of the script plus the two listings:
```
bash /tmp/run_daily_look.sh esports 2>&1 | head -60
ls -l /mnt/HC_Volume_107257520/pkarbs/goalserve/esports_payloads | grep 20261118 | head -30
ls -ld /mnt/HC_Volume_107257520/pkarbs/goalserve/*payloads | head
```
(Re-fetch `feeds/run_daily_look.sh` from origin/claude/project-thread-vg2ckg to /tmp first, as in P47.) Paste under `## F look 1 rerun (19 Nov)`.
5. Confidence 8/10 the relaunch gives matched games; 7/10 on hockey: Goalserve's hockey market names are only partly known, so the preflight prints every accepted and seen name and that is the check.
