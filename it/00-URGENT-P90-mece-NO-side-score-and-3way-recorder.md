# 00-URGENT to IT, 20 Nov 2026 07:05Z (sports MECE NO-side thread). Two rows, P90a first (5 minutes), then P90b (before 12:00Z, football starts from ~11:00Z).

1. **Goal:** find and prove cross-venue/market PK arbs on paper; this row tests whether buying every NO (or every YES, or selling sets) on a mutually exclusive sports set is ever below $1 on each token's OWN asks, with fee 0.05*p*(1-p) and the 1 s taker delay.
2. **Where it stands:** 4-5 Nov both-token captures (8 NHL + 97 CS2 two-way markets, about 530k observations): 0 detections, lowest askA+askB 1.001 (my commit be52bf0544, `reports/sports-mece/no-side-2026-11-20/`). Too thin: those are 2-token markets, the old MECE gaps were in 3-leg football sets, and the 19-20 Nov recorder data is on your storage box where I cannot read it.
3. **The one item:** P90b, the 3-way football both-token recorder. Without it the NO side stays untestable.

## P90a: score the 19-20 Nov pmcs2 and pmdota books (read-only, minutes)
```
V=/mnt/HC_Volume_107257520; mkdir -p $V/pkarbs/mece && cd $V/pkarbs/mece
for f in pair_score.py; do git -C /root/pkarbs show origin/reviewer:it/$f > $f; done   # after git -C /root/pkarbs fetch -q origin reviewer
# run once per folder that holds markets.jsonl + books*.jsonl(.gz): the pmcs2 dir, the pmdota dir, and the raw hours you restored to the storage box (19 Nov 11-22Z)
for D in <pmcs2 dir> <pmdota dir>; do echo "== $D"; systemd-run --scope -p MemoryMax=2G python3 -I pair_score.py $D 2>&1 | tail -12; done
```
Paste the output under `## P90a pair_score (20 Nov)` in `agent/status/goalserve.md`. Expect `detections 0` unless a book is crossed; a non-zero line is the finding, paste its top 4 lines in full. Memory: it holds one folder's rows in RAM (CS2 6 h of 110 tokens was about 280k rows, about 1 GB); if a folder is bigger, run it per day-hour files.

## P90b: slim 3-way football recorder + daily scorer (both tokens of every leg)
**Files (on `reviewer`, `it/`):** `pm_mece_books.js` (needs `pm_cs2_books.js` in the same dir), `test_pm_mece_books.js`, `mece_score.py`, `test_mece_score.py`.
**Disk (estimated, not a promise):** smoke run 20 Nov 06:56-06:58Z, 462 tokens (77 sets, pre-game): 1,758 rows in 148 s, 112 KB gz, so about 2-4 MB/h pre-game. In-play worst case from the 5 Nov NHL tape: about 1,500 rows per token-hour at 34 B/row gz; 240 live tokens gives about 12 MB/h = 0.3 GB/day. Live window is game start -3.5 h to +1 h only. Self-stops under 10 GB free (VOL2 about 12 GB now) AND when its folder passes 3 GB (7 days at the worst case would be 2 GB). Plain files are never written, only gzip members.
```
V=/mnt/HC_Volume_107257520; D=$V/pkarbs/pmmece; mkdir -p $D && cd $D
git -C /root/pkarbs fetch -q origin reviewer
for f in pm_mece_books.js test_pm_mece_books.js pm_cs2_books.js mece_score.py test_mece_score.py; do git -C /root/pkarbs show origin/reviewer:it/$f > $f; done
node test_pm_mece_books.js && python3 -I test_mece_score.py        # both must print PASS
pgrep -f pm_mece_books.js || nohup node pm_mece_books.js $D 2026-12-31T00:00:00Z 10 3 >> stdout.log 2>&1 &
sleep 90; pgrep -f pm_mece_books.js; tail -5 recorder.log; ls -l $D; wc -l markets.jsonl
# daily scorer, from day 1, at 00:35Z and also a partial-day number now (the first interim number is due today):
python3 -I mece_score.py $D $(date -u +%F) --tsv $D/scores.tsv
(crontab -l 2>/dev/null; echo "35 0 * * * cd $D && python3 -I mece_score.py $D \$(date -u -d yesterday +\%F) --tsv $D/scores.tsv >> score.log 2>&1") | crontab -
```
Paste under `## P90b MECE recorder (20 Nov)` in `agent/status/goalserve.md`: test lines, `pgrep`, last 5 recorder.log lines, `scores.tsv`. **Done check:** `recorder.log` shows `ws open, tokens N` with N > 0 once a match is within -3.5 h..+1 h (before that it logs `live-markets=0`, which is not a fault), `books-YYYYMMDDHH.jsonl.gz` grows by 30 s, `scores.tsv` has a line for today.
**Protect:** add `pkarbs/pmmece` and `pkarbs/mece` to the ship_raw exclude list and the protected list (never ship the books whole).
**Live read before the main windows (Nick's rule, 30 min before):** Saturday 21 Nov 11:30Z, 14:30Z and 17:30Z run `pgrep -f pm_mece_books.js; tail -3 $D/recorder.log; ls -l --time-style=full-iso $D/books-*.jsonl.gz | tail -2; sleep 120; ls -l --time-style=full-iso $D/books-*.jsonl.gz | tail -2` and paste. File must grow over the 120 s once a match is live.
**If a step fails:** paste `stdout.log` tail; I re-commit within 30 minutes.

## What the daily line means
`mece_score.py` prints one line per UTC day: sets with all 6 tokens seen, observations, and per variant (buyYES, buyNO, sellYES, sellNO) the lowest cost ratio (or highest proceeds ratio), runs and net $ at detection time (d0) and 1 s later (d1). Everything priced from own asks/bids, fee 0.05*p*(1-p), no NO derived from YES. Not modelled: taker rebate (tier 0%), conversion costs, leg risk. A positive d1 net is a lead, not a result: it needs the independent audit before anyone relays it.
