## P35 — PK ARBS Dota book recorder

- **Disk before:** `df -B1` at 2026-11-18 22:26:33Z: 105089261568 total, 81104748544 used, 18599026688 available. The measured 18.599 GB free exceeded the 17 GB start gate.
- **Recorder:** already running; no duplicate process was started. PID 2249664, started 2026-11-18 21:13:48Z, command uses `pm_dota_books.js` with end time 2026-11-20T09:30:00Z. Output directory: `/mnt/HC_Volume_107257520/pkarbs/pmdota`.
- **15-minute sample:** 22:27:47Z–22:42:47Z. `books.jsonl`: 36,598 bytes / 80 rows at both endpoints (0 bytes, 0 rows added = 0 MB in 15 min). `markets.jsonl`: 48,568 bytes / 119 rows to 49,807 bytes / 122 rows (+1,239 bytes = 0.001239 MB in 15 min). Sample files are retained beside the outputs.
- **Step 3 output:** `ls -l`: books.jsonl 36,598 bytes; markets.jsonl 49,807 bytes; pm_dota_books.js 4,081 bytes; recorder.log 10,821 bytes; sample-start.txt 90 bytes; sample-end.txt 325 bytes. `tail -5 recorder.log`: last five lines were the two Team Lynx vs Spirit Academy Game Winner market discoveries and its BO3 market discovery, all timestamped 2026-11-18T22:28:50.251Z. `wc -l`: 80 books rows, 122 market rows. Coverage check: `conds 2 both_tokens 2`. Sample-end `df -B1`: 105089261568 total, 82483740672 used, 20751085568 available (80%). A later check at 22:44:21Z measured 20746121216 available.
- **Hourly gzip:** installed and verified in Prime crontab: `7 * * * * cd /mnt/HC_Volume_107257520/pkarbs/pmdota && f=books.$(date -u -d "1 hour ago" +\%Y\%m\%d\%H).jsonl && cp books.jsonl $f && : > books.jsonl && gzip -f $f`.
- **Current observation:** process PID 2249664 remained running at 22:44:21Z. The book file did not grow during the 15-minute sample; the measured run therefore establishes both-token coverage for the two recorded conditions, but does not establish ongoing book-row throughput in that interval. No storage-box copy was made.

## P40 extend (2026-11-19)

- At the check on 2026-11-19 01:44:50Z, the requested old PID 2249664 was absent. The current recorder was already running as PID 2539785, started 2026-11-19 01:13:04Z, command `/usr/local/bin/node /mnt/HC_Volume_107257520/pkarbs/pmdota/pm_dota_books.js /mnt/HC_Volume_107257520/pkarbs/pmdota 2026-11-30T00:00:00Z`; its cwd is `/root`.
- Disk availability measured at 01:44:50Z was 18,725,597,184 bytes; the 17 GB start threshold was met at that observation. A pre-launch measurement for the 01:13 start was not captured in this session.
- At 01:47:37Z, PID 2539785 remained live. `recorder.log` ended with three market-discovery lines timestamped 2026-11-19T01:13:04.839Z. Current files then: `books.jsonl` 0 bytes / 0 rows, `markets.jsonl` 95,095 bytes / 233 rows, `recorder.log` 20,663 bytes. No `stdout.log` existed at the requested path. Available disk at 01:47:37Z was 18,323,320,832 bytes.
- The replacement was already running before this session began the P40 check; this session did not signal or relaunch it. The 10:30Z first-window check remains pending.
