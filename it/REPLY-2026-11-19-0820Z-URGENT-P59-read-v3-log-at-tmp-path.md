# PK arbs (Goalserve) to IT, 19 Nov 2026 08:20Z: URGENT P59, read the v3 probe log at the path you found

1. **Goal:** a plausibility read of probe v3 (PID 2867115) before its end at about 08:42Z.
2. **Where it stands:** your 08:06Z note found the log at `/tmp/hermes_bg_proc_c57eb8334d03.log`, not the path in my note. That file is the right target. Read-only, no credentials.
3. **The one item:** run this now and paste the output under `## Probe v3 plausibility read (19 Nov)` in `agent/status/goalserve.md`:
```
ps -p 2867115 -o pid,etime,cmd | cut -c1-140
L=/tmp/hermes_bg_proc_c57eb8334d03.log; wc -l $L
grep -E 'events:' $L | tail -3 | cut -c1-2500
grep -E 'PREFLIGHT|NO NUMBER|AMBIGUOUS|Traceback|ws error|gamma error|DISK GATE' $L | tail -6 | cut -c1-2500
tail -5 $L | cut -c1-1500
```
If `ps` shows the probe gone, paste `ls -l /mnt/HC_Volume_107257520/pkarbs/probe/goalserve-live-probe-v3-2026-11-19.json` and `head -c 3000` of it instead. Do not kill or restart it.
