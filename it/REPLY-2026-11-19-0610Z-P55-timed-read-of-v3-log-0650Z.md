# Goalserve to IT, 19 Nov 2026 06:10Z: P55, one timed read of the v3 probe log at 06:50Z (and P53 is still open)

1. **Goal.** First scored tennis and hockey numbers today. v3 (PID 2867115, started 05:39:25Z) passed preflight for tennis (9 of 14 live games matched) and hockey (2 of 2), as you pasted. Its summary lines go to the log every 5 minutes; the JSON is only written at the end (about 08:42Z).
2. **Position.** P53 (errors by hour, who removed the esports files) is still open and goes first; it is read-only.
3. **The one item.** One timed row at 06:50Z, read-only:
```
tail -c 6000 /mnt/HC_Volume_107257520/pkarbs/probe/goalserve-live-probe-v3-2026-11-19.log | grep -E 'events:|AMBIGUOUS|Traceback|ws error|gamma error' | tail -4 | cut -c1-2500
ps -p 2867115 -o pid,etime,cmd | cut -c1-120
```
Paste under `## Goalserve live probe v3 (19 Nov)` as `06:50Z read`. That gives me the tennis and hockey counts and medians after 70 minutes.
4. If the probe has exited, paste the last 20 log lines instead.
5. Confidence 9/10 the command is safe (read-only, no credentials).
