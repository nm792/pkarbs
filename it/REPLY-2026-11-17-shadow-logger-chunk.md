# Reply to IT: shadow logger chunk (unit, command, restart path) and the gamma 406 answer, 17 Nov 2026 10:05Z

1. **Goal:** find and build automated Polymarket edges worth $500/day with no catastrophic loss.
2. **Where we stand (measured):** no validated edge. The sports MECE NO side is untested: no NO-token book was ever recorded (PRs #393 and #394 on `claude/project-thread-vg2ckg` add it; offline tests only, nothing run on the box).
3. **The one item that matters most:** the shadow logger is NOT running and has not been since 4 Nov, so there is no running unit to restart and the 406 never affected a live capture. My earlier note's "same flags as now" was wrong and is withdrawn. Nick stopped it on 3 Nov ("OK" at 14:15Z, `agent/inbox/2026-11-03-stop-shadow-logger-approved.md`) with "do not start any replacement", and `agent/status/sports-mece-shadow.md` says do not restart without a new reviewer note. So P16 must not START until Nick says yes (decision card posted to him now); queue it as held.

**Evidence from the repo (your own 11 Nov check, `agent/outbox/thesports-shadow-logger-stop-hash-check-2026-11-11.md`):** unit `pkarbs-shadow-logger.scope` not found, no `shadow_logger.py` process, `data-v2/raw-2026110400.jsonl.gz` last written 2026-11-04 00:56:26Z, `events.jsonl` 00:56:07Z. The 406 answer: gamma has required gzip for pages over 50 since some time I cannot date; the logger was already stopped before it could have mattered, so no capture was lost to it. I could not see box logs, so when the 406 began is unknown.

**The chunk (read-only, run now; outputs unedited into status/):**
```
systemctl list-units --all --no-pager 'pkarbs-*' ; systemctl list-units --type=scope --all --no-pager | grep -i shadow
tmux ls 2>&1 | head ; pgrep -af shadow_logger
ls -la --time-style=full-iso /mnt/HC_Volume_107257520/pkarbs/shadow/data-v2/ | tail -5
df -B1 / /mnt/HC_Volume_107257520
```

**How it was started before (from the 3 Nov note and the original task `agent/TASK-sports-mece-shadow.md`):** a systemd-run scope named `pkarbs-shadow-logger.scope`, command `python3 shadow/shadow_logger.py --out /mnt/HC_Volume_107257520/pkarbs/shadow/data-v2/` (defaults only: in-play window 4 h, gamma refresh 120 s, REST resync 60 s, min edge 0; no `--lead-h`), needs `pip install websockets`. Restart path if Nick approves: update the repo to `claude/project-thread-vg2ckg` at or after the #394 merge (2e92b5c9c5), run `python3 shadow/test_no_subscription.py` and `python3 shadow/test_gates.py` (expect ALL PASS and 25 of 25), then the same systemd-run line with a new output dir `data-v3/` on the volume. Stop path: `systemctl stop pkarbs-shadow-logger.scope`.

**Cost to decide on:** the first run wrote about 1 MB gz per minute at ~600 books; with NO tokens expect about 2x, roughly 3 GB a day, so the volume's 43.5 GB free lasts about two weeks; set a watch at 15 GB free. Nothing is written to root.

Confidence 8/10 on the facts above (all from the repo's own notes and files); unknown: the current box state until your chunk output is back, and whether Nick approves the restart.
