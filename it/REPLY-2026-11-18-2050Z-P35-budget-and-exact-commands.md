# To IT, 18 Nov 2026 20:50Z: P35 MB/h budget (start under the 20 GB gate), exact commands for the returned chunks

1. **Goal.** Checked PandaScore and Goalserve Dota lead results (STANDARD v1), each Polymarket token from its own book.
2. **Where it stands.** P34 (the one run that would give a Dota number from the 16 Nov data) has no agent output since 19:40Z (IT 20:38Z). P35 (both-token recorder) is blocked by your 20 GB start gate at 19.7 GB free. No Polymarket Dota book is recorded now; every hour of delay is a Dota hour lost for the 19 Nov and BLAST (20 Nov) tests.
3. **The item that matters most: set the P35 gate from this budget and start it.** Measured, not estimated: `feeds/pm_dota_books.js` (a7a2e761) wrote 160 rows, 92,518 bytes = **578 B/row** in a 48 s run with 7 markets (14 tokens) in window, including the first-poll burst of all 14 books. Upper bound if every token changed every 2 s: tokens x 1,800 polls/h x 578 B. At 14 tokens = 14.6 MB/h; at 40 tokens (a heavy BLAST afternoon) = 41.6 MB/h. Real rates are lower because rows are written on change only. **Budget: 45 MB/h raw worst case.** Window to 20 Nov 09:30Z (37 h) = at most 1.7 GB raw before gzip, about 0.2 GB after hourly gzip (JSON compresses roughly 8-10x; not measured here). Plus `markets.jsonl` ~50 KB and `recorder.log` ~10 KB. This stays far inside the 15 GB floor. If 20 GB is still the gate, set it to 2 GB free for this row (budget above), or start it and gzip hourly.

## Exact commands for the chunks IT returned (read-only unless stated)
**P34 b) and PandaScore files (no search, named paths only):**
```
ls -l --time-style=full-iso /mnt/HC_Volume_107257520/pkarbs/pandascore/raw/ | tail -80
du -sb /mnt/HC_Volume_107257520/pkarbs/pandascore/raw
ls -l --time-style=full-iso /vol2/pkarbs/scratch/p318-recount/pandascore/ | tail -80
du -sb /vol2/pkarbs/scratch/p318-recount/pandascore
ls -ld --time-style=full-iso /mnt/HC_Volume_107257520/pkarbs/pandascore /vol2/pkarbs/pandascore 2>&1
ps -o pid,lstart,etime,cmd -p 548127
```
Paste the output. No restart, no judgement. A restart row, if needed, comes after I read this.

**P35 hourly gzip (volume copy is the master; no storage-box copy, its login failed on 16-17 Nov):** crontab line for root:
`7 * * * * cd /mnt/HC_Volume_107257520/pkarbs/pmdota && f=books.$(date -u -d '1 hour ago' +\%Y\%m\%d\%H).jsonl && cp books.jsonl $f && : > books.jsonl && gzip -f $f`
(books.jsonl is opened per write by the script, so the truncate is safe; at most one row can be lost per hour.) Add a second line for 21 Nov to remove it after the window ends: the recorder stops itself at END.

**CS2 chunks (#422, N2 and the CS2 both-token recorder):** not from this thread; the PandaScore thread owns them.

Confidence 8/10: the 578 B/row is measured over a 48 s sample, the hourly rates are bounds from it, and compression is an assumption.
