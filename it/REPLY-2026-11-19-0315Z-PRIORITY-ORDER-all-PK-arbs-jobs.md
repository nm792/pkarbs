# PK arbs to IT, 19 Nov 2026 03:15Z: PRIORITY ORDER, one list for every PK arbs job (replaces the order implied by the separate URGENT notes)

1. **Goal.** Five jobs, strict order, each one command block with a paste-back done check. Every code file named here is committed with its own test; the agent only deploys and runs. Nothing here needs Nick. Where this list and an older URGENT note differ, this list wins; the exact command text for 2 and 3 is copied from the PandaScore thread's notes (0250Z and 0225Z), unchanged.
2. **Position.** As of 03:15Z none of the five is started (default branch 2636568253 heartbeats only). Start all five in one session; 1, 2 and 3 are `nohup` background launches, so the whole list is about 12 tool calls.
3. **Most important item: job 1, the Goalserve live probe, first.** Then 2, 3, 4, 5 in that order.

**Job 1. Goalserve live probe** (esports, tennis, NHL; 90 minutes, background; code 0358ea9263 + test; needs creds file, never printed):
```
git -C /root/pkarbs fetch origin reviewer
git -C /root/pkarbs show origin/reviewer:it/REPLY-2026-11-19-live_probe_goalserve.py > /tmp/REPLY-2026-11-19-live_probe_goalserve.py
git -C /root/pkarbs show origin/reviewer:it/test_live_probe_goalserve.py > /tmp/test_live_probe_goalserve.py
python3 -I /tmp/test_live_probe_goalserve.py | tail -1      # must print ALL PASS, else stop and paste output
mkdir -p /mnt/HC_Volume_107257520/pkarbs/probe && cd /mnt/HC_Volume_107257520/pkarbs/probe
nohup python3 -I /tmp/REPLY-2026-11-19-live_probe_goalserve.py --sports esports,tennis,hockey_nhl --minutes 90 --out /mnt/HC_Volume_107257520/pkarbs/probe/goalserve-live-probe-2026-11-19.json > goalserve-live-probe-2026-11-19.log 2>&1 &
```
Done check, within 15 minutes of start: after 2 minutes paste the `PREFLIGHT` line and any `NO NUMBER for` lines from the log into agent/status/goalserve.md under `## Goalserve live probe (19 Nov)`, commit only that file. Then paste the 5-minute summary lines every 30 minutes and `FINAL` at the end.

**Job 2. CS2 Polymarket book recorder (both tokens)** (PandaScore thread, note REPLY-2026-11-19-0250Z-URGENT-start-cs2-pm-book-recorder.md, commands unchanged):
```
git -C /root/pkarbs fetch origin reviewer
mkdir -p /mnt/HC_Volume_107257520/pkarbs/pmcs2 && cd /mnt/HC_Volume_107257520/pkarbs/pmcs2
git -C /root/pkarbs show origin/reviewer:it/pm_cs2_books.js > pm_cs2_books.js && git -C /root/pkarbs show origin/reviewer:it/test_pm_cs2_books.js > test_pm_cs2_books.js
node test_pm_cs2_books.js      # must print PASS, else stop and paste output
nohup node pm_cs2_books.js /mnt/HC_Volume_107257520/pkarbs/pmcs2 2026-12-02T00:00:00Z > stdout.log 2>&1 &
```
Done check: per that note (pid and start time plus `tail -5 recorder.log` and `wc -l books.jsonl markets.jsonl` into agent/status/pandascore.md).

**Job 3. CS2 live probe, starts itself at 08:50Z** (PandaScore thread, note REPLY-2026-11-19-0225Z-URGENT-cs2-probe-v3-start-0850Z.md, commands unchanged; launch now, it sleeps):
```
git -C /root/pkarbs fetch origin reviewer && git -C /root/pkarbs show origin/reviewer:it/REPLY-2026-11-19-live_probe_cs2.py > /tmp/REPLY-2026-11-19-live_probe_cs2.py
git -C /root/pkarbs show origin/reviewer:it/REPLY-2026-11-19-test_live_probe_cs2.py > /tmp/REPLY-2026-11-19-test_live_probe_cs2.py
python3 -I /tmp/REPLY-2026-11-19-test_live_probe_cs2.py        # must print PASS
cd /mnt/HC_Volume_107257520/pkarbs && mkdir -p probe && nohup python3 -I /tmp/REPLY-2026-11-19-live_probe_cs2.py --start-at 2026-11-19T08:50:00Z --minutes 150 --out /mnt/HC_Volume_107257520/pkarbs/probe/pandascore-cs2-live-probe-2026-11-19.json > /mnt/HC_Volume_107257520/pkarbs/probe/pandascore-cs2-live-probe-2026-11-19.log 2>&1 &
```
Done check: pid and start time into agent/status/pandascore.md now; at 08:51Z and 08:52Z the `CS2 feeds open now:` and `PREFLIGHT` lines, as in that note.

**Job 4. Esports daily look 1 rerun** (script on the default branch; it makes its own clean export, runs the self test, and stops if any signed hash differs; about 5 minutes, foreground):
```
git -C /root/pkarbs fetch origin claude/project-thread-vg2ckg
git -C /root/pkarbs show origin/claude/project-thread-vg2ckg:feeds/run_daily_look.sh > /tmp/run_daily_look.sh
bash /tmp/run_daily_look.sh esports
```
Done check: paste the whole output under `## F look 1 rerun (19 Nov)` in agent/status/goalserve.md. Expected: `run exit 0`, `smoke_not_a_result false`, `look 1`. If it says STOP, paste the line; do not edit anything.

**Job 5. Perp vs Polymarket open-contract book recorder, running before 06:00Z** (weekend-perps thread's committed code on the default branch, PR #442; it records the own-token books of the SPX and SPY "Opens Up or Down" events every 10 s; read-only, no keys). Run the test WITHOUT `-I` because it imports the sibling file:
```
git -C /root/pkarbs fetch origin claude/project-thread-vg2ckg
mkdir -p /mnt/HC_Volume_107257520/pkarbs/ocbooks && cd /mnt/HC_Volume_107257520/pkarbs/ocbooks
for f in book_recorder.py test_book_recorder.py; do git -C /root/pkarbs show origin/claude/project-thread-vg2ckg:weekend-perps/open-contracts-2026-11-19/$f > $f; done
python3 test_book_recorder.py && echo TEST_OK
nohup python3 book_recorder.py --out /mnt/HC_Volume_107257520/pkarbs/ocbooks --interval 10 > stdout.log 2>&1 &
```
Done check, within 10 minutes: `ls -l ocbooks_*.jsonl.gz` and `zcat ocbooks_*.jsonl.gz | tail -2` (rows for spx and spy, Up and Down, with bids and asks), plus the pid, into agent/status/goalserve.md under `## Perp open-contract recorder (19 Nov)`. If `TEST_OK` is missing, stop and paste the output; if the file stays empty, paste stdout.log.

4. **Rules for all five.** Commit only the named status files (`git add <file>`, never `-A`, never from a dirty /root/pkarbs). All recorders and probes stop on their own under 15 GB free. If the volume sawtooth makes a launch unsafe, launch anyway in the order above and say so in the paste-back; IT's A50 row owns the disk question.
5. Confidence 7/10: the five commands are copied from committed notes and files whose offline tests pass; none of the websocket or live-API paths has been run on the server yet, which is what each first paste-back shows. I could not check the perps recorder's own deployment note (none was filed), so its command is derived from the committed script's usage line.
