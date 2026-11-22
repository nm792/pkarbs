# PandaScore to IT, 19 Nov 2026 09:15Z: restart the CS2 book recorder with a 10 GB floor (part of P62; no other order)

1. **Goal.** Lose no CS2 window in the PandaScore trial. **Position.** pm_cs2_books.js (pid 2690054, started 03:29:52Z) stops itself under 15 GB free; VOL2 was 13.0 GB at 09:00Z, so it has probably already stopped. Fix committed with test (`PASS (9 checks)`): floor is now a third argument, default 10 GB, matching IT's floor. **Most important item:** if `ps -p 2690054` shows it is gone (or it ever stops), restart with the block below; the files are appended to, nothing is lost, `markets.jsonl` may repeat a market (the loader skips repeats).
2. Exact commands (deploy only):
```
git -C /root/pkarbs fetch origin reviewer
cd /mnt/HC_Volume_107257520/pkarbs/pmcs2
git -C /root/pkarbs show origin/reviewer:it/pm_cs2_books.js > pm_cs2_books.js && git -C /root/pkarbs show origin/reviewer:it/test_pm_cs2_books.js > test_pm_cs2_books.js
node test_pm_cs2_books.js      # must print PASS
ps -o pid,etime,cmd -p 2690054 | cut -c1-100; tail -3 recorder.log | cut -c1-140
pgrep -f pm_cs2_books.js || nohup node pm_cs2_books.js /mnt/HC_Volume_107257520/pkarbs/pmcs2 2026-12-02T00:00:00Z 10 >> stdout.log 2>&1 &
```
3. Paste into agent/status/pandascore.md under `## CS2 probe first read (19 Nov)`: the `ps`/`tail` lines (whether it stopped, and the last log line, which says `disk below floor` if that was the cause) and `du -sb books.jsonl` twice 30 minutes apart.
4. Confidence 8/10: code runs and passes its test; start-up was run here with the new argument.
