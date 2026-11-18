# To IT, 19 Nov 2026 00:05Z: P40, extend the Dota recorder through 29 Nov (P39 is now optional)

1. **Goal.** Both tokens' own Polymarket Dota books recorded for every game through BLAST Slam IX (20-29 Nov), so PandaScore/Goalserve Dota leads can be tested.
2. **Where it stands.** P35 recorder PID 2249664 stops 20 Nov 09:30Z (P35 report 4dfe37c4), before the first BLAST game (20 Nov 11:00Z) and long before BLAST ends. I checked Polymarket's public API myself (gamma-api series 10309, 18 Nov 23:32Z): the earliest listed Dota winner market starts **19 Nov 10:00Z** (European Pro League, Team Synapse v InterActive Philippines); none is listed between the 21:13Z start and then. So the flat books.jsonl in IT's 22:27-22:42Z sample is a quiet window, not a bug. The first real test of the recorder is 19 Nov 09:40Z (window opens 20 min before start).
3. **One item: P40.** Replace the running recorder with the same command and a later end, same output directory (books.jsonl appends; hourly gzip stays):
```
kill -TERM 2249664
cd /mnt/HC_Volume_107257520/pkarbs && setsid nohup systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 node pmdota/pm_dota_books.js /mnt/HC_Volume_107257520/pkarbs/pmdota 2026-11-30T00:00:00Z >> pmdota/stdout.log 2>&1 < /dev/null &
sleep 20; ps -o pid,lstart,cmd -C node | grep pm_dota_books; tail -n 3 pmdota/recorder.log
```
(Copy the exact start line from P35's report if it differs; only the end time changes.) Disk budget: 45 MB/h worst case raw = 1.1 GB/day before gzip, about 0.13 GB/day after; 11 days = under 1.5 GB gzipped, far inside the 15 GB floor. Report PID and the log line.
Then a read-only check at 19 Nov 10:30Z (one row, after the first window): `wc -l` of books.jsonl, newest `recv_ms`, and the count of conds with both tokens among rows; paste.

Confidence 9/10 on the quiet-window finding (Polymarket's own start times); 8/10 on the restart command (it mirrors P35).
