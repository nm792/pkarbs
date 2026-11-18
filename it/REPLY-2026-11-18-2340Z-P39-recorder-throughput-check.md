# To IT, 18 Nov 2026 23:40Z: P39, one read-only check that the Dota recorder is writing (exact commands)

1. **Goal.** Polymarket Dota books for both tokens, continuously, so PandaScore/Goalserve Dota leads can be tested on 19-21 Nov (BLAST from 20 Nov).
2. **Where it stands.** P35 (pkarbs 4dfe37c4): recorder PID 2249664 running since 21:13:48Z; both-token coverage OK for 2 conds; but books.jsonl stayed at 80 rows / 36,598 bytes for 15 min (22:27-22:42Z). No Dota book rows or an hourly gzip is the question; recorder.log shows discovery only.
3. **One item: P39.** Read-only, one session, paste output:
```
cd /mnt/HC_Volume_107257520/pkarbs/pmdota
date -u +%FT%TZ
ls -l --time-style=full-iso
wc -l books.jsonl markets.jsonl
for f in books.2026111*.jsonl.gz; do echo $f $(zcat $f | wc -l); done
tail -n 3 books.jsonl | cut -c1-330
grep -c "gamma status" recorder.log; grep -c "book error" recorder.log; tail -n 8 recorder.log
ps -o pid,lstart,etime,rss,cmd -p 2249664
```
Report rows per hour and the timestamp (`recv_ms` converted) of the newest book row. If books.jsonl is not growing and Dota games are live (check the PandaScore latest file for a Dota match `running` in the last hour, `ls -l` only), the recorder is stuck: say so and do not restart without a row; I send the fix. A quiet hour with no Dota game in the window [start -20 min, +5 h] is normal; state which case it is from the markets' `start` values for the 2 conds (`grep` of the cond lines in markets.jsonl `start` field).

Confidence 8/10 that a quiet window explains it; this check separates that from a bug.
