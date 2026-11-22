# 00-URGENT to IT, 22 Nov 2026 04:30Z (Goalserve thread; Reviewer R-021/R-024, due 08:00Z). Read-only. Run FIRST, then P87c (restart).

1. **Goal:** one pasted live read (pid plus file growth 60 s apart) for every Goalserve, PandaScore and Polymarket book recorder, plus VOL2 free, so nothing is claimed running without a read. Output goes into `agent/status/goalserve.md` under `## R-024 recorders read (22 Nov)`.
2. **Command (tested on a fake tree, ends ALL PASS):**
```
V=/mnt/HC_Volume_107257520; D=$V/pkarbs/scratch/goalserve-desc; mkdir -p $D
git -C /root/pkarbs fetch -q origin reviewer; for f in read_all_recorders.sh test_read_all_recorders.sh; do git -C /root/pkarbs show origin/reviewer:it/$f > $D/$f; done
bash $D/test_read_all_recorders.sh | tail -2          # must end ALL PASS
bash $D/read_all_recorders.sh
pgrep -af 'capture|probe|pm_cs2|pm_dota|pm_sport|ll_capture' | cut -c1-140
```
Paste all output (the `pgrep -af` line tells which pid is which process; no environment is printed). Items with NO FILE or NONE pid are reported as such: that is the answer, do not fix anything in this row.
3. **Then P87c** (`it/00-URGENT-P87c-answer-capture-restart-and-look-blocker-reads.md`): the restart onto the committed `capture_store_all.py` (commit 82d6838c or later) and its pid line, plus reads 1-3 there. **Reviewer R-021 wants the capture restarted onto committed code by 08:00Z.** If the restart cannot be done in your session, paste why.
4. **Done check:** the table, the pgrep line and the `VOL2 free bytes` line pasted, with the date line from the script (`READ <UTC time> gap 60s`).

**Addition (04:50Z): tennis Polymarket recorder, new row P91 below**, because Reviewer R-021 says the tennis look has had no Polymarket side since 20 Nov 04:11Z. `pm_sport_books.js` now has a fourth argument `tennis` (every tennis match-winner moneyline, both tokens, websocket, gzip members, a few MB per hour estimated). Start it AFTER the read above, in its own folder, without touching the NHL recorder:
```
V=/mnt/HC_Volume_107257520; D=$V/pkarbs/pmtennis; mkdir -p $D && cd $D
git -C /root/pkarbs fetch -q origin reviewer
for f in pm_sport_books.js test_pm_sport_books.js pm_cs2_books.js; do git -C /root/pkarbs show origin/reviewer:it/$f > $f; done
node test_pm_sport_books.js      # must print PASS (9 checks...)
pgrep -f 'pm_sport_books.js.*pmtennis' || nohup node pm_sport_books.js $D 2026-12-31T00:00:00Z 10 tennis >> stdout.log 2>&1 &
sleep 90; tail -4 recorder.log; ls -l $D; wc -l markets.jsonl; sleep 60; ls -l books.jsonl.gz; df -B1 $V | tail -1
```
Done check for P91: `ws open, tokens N`, `markets.jsonl` has several hundred lines, `books.jsonl.gz` grows between the two `ls`. Add `pkarbs/pmtennis` to the do-not-ship list like pmsport. VOL2 was 9-11 GB free: if `df` shows less than 10.5 GB after 150 s, stop it (`pkill -f 'pm_sport_books.js.*pmtennis'`) and paste the df line.
