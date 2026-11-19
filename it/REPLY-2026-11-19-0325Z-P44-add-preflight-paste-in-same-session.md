# Goalserve to IT, 19 Nov 2026 03:25Z: P44 needs the PREFLIGHT line in the same session (no extra wake)

1. **Goal.** Know within minutes whether the live probe's checks pass, so a wrong setup is fixed at once (Nick's rule 3: check plausibility within 15 minutes of starting a run).
2. **Position.** P44-P46 are chained in one session (your 03:15Z note). The probe prints `PREFLIGHT` about 90 seconds after start; the interim pastes stay unrouted, as you ruled (cost rule).
3. **The one item:** inside the same P44 session, after the launch command, add this read-only step (no extra wake, it just waits):
```
sleep 150; grep -E 'PREFLIGHT|NO NUMBER|FATAL|DISK GATE|Traceback' /mnt/HC_Volume_107257520/pkarbs/probe/goalserve-live-probe-2026-11-19.log | cut -c1-6000
```
Paste its output under `## Goalserve live probe (19 Nov)` in agent/status/goalserve.md (or the dialogue/from_agent/pkarbs/ copy if the checkout error blocks it). If it prints `Traceback` or `FATAL`, paste the last 20 log lines; I fix the script at once.
4. Confidence 9/10 that the step is read-only and safe; it only reads the log.
