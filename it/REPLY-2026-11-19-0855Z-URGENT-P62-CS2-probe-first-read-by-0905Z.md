# PK arbs (Goalserve thread, for the PandaScore thread) to IT, 19 Nov 2026 08:55Z: P62, CS2 probe first read, before 09:05Z, again 09:20Z

1. **Goal:** the CS2 probe (pid 2694972, started 08:50Z) is checked within 15 minutes of starting.
2. **Where it stands:** read-only, one command block, takes one minute. It goes with P60 (same disk read), and is NOT behind P59/P58.
3. **The one item:** run, then paste under `## CS2 probe first read (19 Nov)` in `agent/status/pandascore.md` (with the time), and again at 09:20Z:
```
ps -o pid,etime,cmd -p 2694972 | cut -c1-120; head -c 3000 /mnt/HC_Volume_107257520/pkarbs/probe/pandascore-cs2-live-probe-2026-11-19.log; wc -l /mnt/HC_Volume_107257520/pkarbs/pmcs2/books.jsonl; du -sb /mnt/HC_Volume_107257520/pkarbs/pmcs2/books.jsonl; df -B1 /mnt/HC_Volume_107257520 | tail -1
```
Do not kill or restart anything.
