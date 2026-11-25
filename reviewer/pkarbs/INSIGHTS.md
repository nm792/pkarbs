# PK arbs: INSIGHTS (one place, used, not filed and forgotten)

Rule (Nick 25 Nov 03:52Z): every PK insight goes here, the turn it is found. Each entry has a date, the insight, the evidence, and **what it changed**. An entry whose "Used by" says "nothing yet" has a dated next action, and that action is a row in PK-STRATEGY-STATUS.md. Every scoring run, spec and IT note starts by reading this file. Superseded entries are struck through and left in place, never deleted.
Moved here 25 Nov 04:10Z from: PK-STRATEGY-STATUS.md, REAUDIT-2026-11-22, DISCARDED-AUDIT-2026-11-23, REPLY-2026-11-23-late-resolving-scan, mentions-screen-2026-11-25, mentions-dell-2026-11-24, rn1-cs2-timing-2026-11-25, rn1-recheck-2026-11-24, IT reports P143/P151/P153, pipeline/R036/INBOX-row-P-019 (branch claude/project-thread-o5rbz8). Those files stay as the evidence.

## Index
- Process and plumbing: I-1 to I-6
- Will-say / mentions: I-10 to I-17
- Trial feeds (PandaScore, Goalserve) and CS2: I-20 to I-26
- RN1 / soccer / NBA: I-30 to I-33
- Late-resolving, MECE, macro, perps, other: I-40 to I-48

## Process and plumbing
| ID | Date | Insight | Evidence | What it changed / used by |
|---|---|---|---|---|
| I-1 | 25 Nov | Data was being recorded but never scored. IT lane P takes only `open` rows; every PK row was `waiting`, so the lane sat idle from 24 Nov 20:54Z | PASS-P.tsv "idle: no open P rows" every 30 min | Every scoring request is now an `open` row with a time (IT-OPS 0135Z, 0145Z); daily standing row P152 at 06:00Z |
| I-2 | 25 Nov | ~~Recorded hours can disappear with no known mover.~~ Superseded by I-7 (most likely shipped to the box). Original note: PandaScore raw 24 Nov 13Z/14Z, events.jsonl.gz and pmcs2 markets 13Z/14Z were listed at 15:20Z 24 Nov and gone by 02:50Z 25 Nov; the only pmcs2 cleaner (T104 retention, 3-day, verify-then-unlink) did not list them | P151, P153 reports (dialogue/from_agent/pkarbs/) | Any scoring row must first copy its input hours to a dated scratch folder on VOL2 before scoring. To add to P152 and every future scoring note. 04:30Z: capture code has no delete/rename (checked); 16 Nov file also gone, earliest survivor is 22Z 24 Nov, IT floor change ~21:45Z 24 Nov = first window to check. Forensic row P154 filed (IT-OPS 0430Z, 8b41c2e26): dir stat times, every cleaner/IT disk action, journals, histories, open fds, storage box, git, snapshots, plus a guard |
| I-3 | 25 Nov | The old PandaScore capture never closes its hour file: at 03:24Z 25 Nov it was still writing `pandascore_2026112422` (24 KB after 5.5 h) | P153 step 1 | Confirms the v4 watchdog (hour close, heartbeat) is needed; P143 deploy reopened 03:47Z |
| I-4 | 25 Nov | Root disk floor (5 GB) blocks starts; root at 4.05 GB. IT ruled 03:47Z that the floor does not gate a sub-50 MB install (root >= 3 GB) | P143 02:22Z refusal; IT 03:47Z commit b5666f2ca | Small installs go ahead; recorder starts write to VOL2 |
| I-5 | 24-25 Nov | Owner threads go silent; deadlines slip unless the Reviewer does the work | INBOX last row P-PS-042 at 15:25Z 24 Nov | Reviewer works the ledger itself (PK-STRATEGY-STATUS section D) |
| I-7 | 13-17 Nov, re-found 25 Nov 05:10Z | Recorder hour files do NOT stay local. `/root/ship/ship_raw.sh` (every 30 min, folders registered in `/root/ship/writers.conf`, pandascore included) ships each closed hour to the storage box and deletes the local copy ~90 min after close. Only BADGZ files stay (e.g. pandascore_2026111612). "Missing locally" = check the box first. This was known on 16-17 Nov and forgotten, which caused the 25 Nov "lost recordings" alarm | agent/status/goalserve.md ~l.222-223; it/IT-2026-11-17-p15c-gate-shipper.md item 3; agent/inbox/TO-IT-URGENT-pandascore-raw-hours-missing-2026-11-16-2020Z.md; P154 debugfs listing | P155 (IT-OPS 0515Z, 1af739f3a): read ship.log + box with the shipper's own transport, copy 24 Nov 13-14Z back, rerun P151. Every scoring note must pull inputs from the box like feeds/run_ps_cs2_daily_look.sh does. CONFIRMED 05:23Z (P155): 24 Nov 13Z/14Z PandaScore hours and events are on the box, gzip PASS, copied to tmp/P155. Shipper safety (SHIP-SAFETY 06:03Z): deletes only after rsync success + checksum match; box refused once (04:30Z run, nothing deleted), recovered 05:00Z. pmcs2 is not a shipper writer |
| I-8 | 25 Nov 06:25Z | The PandaScore-vs-pmcs2 scorer reads ONE cumulative `pmcs2/markets.jsonl`, not hourly `markets-*.jsonl.gz`. The "missing markets files" in P151/P154 never existed; my P151 note named the wrong inputs | feeds/ps_kills_vs_pmcs2.py lines 4, 62 | P151b rerun on box copies + markets.jsonl (IT-OPS 0630Z, a08838b44). Every scoring note now names inputs from the scorer's own code |
| I-9 | 25 Nov 07:30Z | (a) Prime load (9-11 at 06:20-06:51Z) is above the 3.2 gate, so PK scoring rows (P150, P146-P149) keep getting capacity-retried; (b) copies under VOL2 `tmp/` can vanish within 2 h (tmp/P155 gone by 06:51Z) | P150 row; P151b report | Scratch for PK rows goes under `pkarbs/scratch/`; copy steps may run above the gate (no CPU). Load cause to be read from the IT router |
| I-6 | 17 Nov | A test on 5-minute bars cannot measure a seconds delay; "no edge" from it is about bars only | SETTLED B.1 | Every delay/lead test runs finer than the delay and carries a planted case (P105, v3, P152) |

## Will-say / mentions (top PK priority by $ volume)
| ID | Date | Insight | Evidence | What it changed / used by |
|---|---|---|---|---|
| I-10 | 25 Nov | Volume is Trump. 30-day mention-markets volume $1,390,588 over 67 events: Trump $1.12M (81%), other $138K (10%), earnings calls $113K (8%), creators $18K (1%) | mentions-screen-2026-11-25/vol.py, README s.1 | Ranking by volume x edge; Trump month/trip base rate is the next screen; earnings-only tests are no longer the main line |
| I-11 | 23 Nov | Old tests covered mostly earnings calls (7.5% of volume) and were print-sized: $4.9/day was a stake cap, not an edge verdict. Lifting the one-print limit: +$2.00/day to +$13.31/day on the same 30 days | DISCARDED-AUDIT row 1; REAUDIT row 1 | Old FLOOR is not a result; the WS paper logger (P121) sizes against own-token asks |
| I-12 | 24 Nov | The frozen 10c base-rate rule placed no bet on the Dell call: own-token asks were never 10c under the base rate | mentions-dell-2026-11-24 (18753603f5) | Edge definition widened to the whole family and own-ask ladders (screen.py) |
| I-13 | 23-25 Nov | Count markets ("AI 50+ times") were pooled with plain-word markets because the word key strips digits. The fix flag KEEP_THRESHOLD exists in the deployed scorer (sha 5e44c570) but is OFF by default | OPEN-ITEMS 25; screen_kt.py; L5 check 25 Nov | With it on, the screen is 14 tokens / $2,634 vs 11 / $1,375, and Jensen "AI (30+)" flips to NO. Next: P147 scores both settings, then a fix-on-the-fly flip if on is right |
| I-14 | 25 Nov | A cross-company fair fails the speaker test: Salesforce "Data Center" top row uses a fair pooled across companies | README s.5 | Per-speaker base rates required before any speaker market is used: webb T111 (Salesforce last 4 calls, Jensen last 4 keynotes) |
| I-15 | 25 Nov | Forward test so far: 6 resolved bets, 1 win, -$26.51 | forward_LATEST.txt | Too few to judge; kept running; P147 scores the P121 decisions |
| I-16 | 25 Nov | Gamma "open" lists include ended events (Oct NFL announcer events) | screen_open_kt.json end dates | Screens filter on end > now |
| I-17 | 25 Nov | The gamma tag that works is `tag_slug=mention-markets` ("mentions" returns 0) | vol.py | Used in vol.py / screen.py |

## Trial feeds and CS2
| ID | Date | Insight | Evidence | What it changed / used by |
|---|---|---|---|---|
| I-20 | 25 Nov | No trial feed has a valid lead/lag measurement yet; that, not new feeds, is the PK blocker | Nick 01:29Z; TOP PRIORITY table | No new feeds (no GRID) until PandaScore and Goalserve are timed; P152 daily |
| I-21 | 24 Nov | Goalserve v3 needs 12 sizing matches per cell before any test; NHL had 5 at 14:00Z 24 Nov (placebo not OK) | v3-nhl.json, P144 | P150 NHL not before 06:00Z 25 Nov to include the night slate |
| I-22 | 24 Nov | pmcs2 hour 2026112322 is missing; any CS2 window crossing it fails | P144/P150 | CS2 window starts 23 Nov 23:00Z |
| I-23 | 24 Nov | Old PandaScore +0.83c gross came from a buggy scorer: not a result | REVIEW-2026-11-22-sports-esports-feeds | Only P105-method with planted case counts |
| I-24 | 24 Nov | CS2 = fast-data TAKER edge (RN1 +2.3c/30 s, +2.8c/5 min after his takes; +$115K on $956K, +12%, 73 matches, CI incl. 0) | rn1-recheck-2026-11-24; SETTLED | CS2 maker work stopped. Nick handles faster-feed sourcing; not raised |
| I-25 | 24-25 Nov | RN1 take times vs our PandaScore hours: overlap 0 twice (1 RN1 CS2 take since 24 Nov, 12:29Z, outside captured hours) | rn1-cs2-timing-2026-11-25 | Rerun only once the v4 capture covers full days |
| I-26 | 23 Nov | OddsPapi/Pinnacle lead is 1-2 s, inside Polymarket's 1 s sports taker delay | REVIEW-2026-11-22-sports-esports-feeds | Parked; reopens with finer windows |

## RN1, soccer, NBA
| ID | Date | Insight | Evidence | What it changed / used by |
|---|---|---|---|---|
| I-30 | 24 Nov | RN1's NBA is about 0 EV (+0.19% on $4.1M); our NBA maker held-out -11.5% [-28.1, +5.2] on 39 games | SETTLED S1 (Nick 09:50Z) | NBA maker closed; P141 not run; never re-asked |
| I-31 | 24 Nov | RN1 soccer maker has no copyable rule: L1 +4.5%, SA +3.8%, CIs span 0, negative without his best 5 markets | rn1-recheck-2026-11-24 | Soccer maker spec must rank by edge per competing maker; recorders P139b from 27 Nov |
| I-32 | 24 Nov | Soccer taker side is small: SA +$15.8K on $151K; L1 -$0.5K | same | L17 soccer taker probe (ledger) |
| I-33 | 17 Nov | Each Polymarket token is its own book; price only from its own asks; mirroring only on resolved books | SETTLED A.1 | Every scorer and screen uses own-token asks |

## Late-resolving, MECE, macro, perps, other
| ID | Date | Insight | Evidence | What it changed / used by |
|---|---|---|---|---|
| I-40 | 22 Nov | Late-resolving: summed causal floor flips sign with lead time (T-3h -$167/day, T-1h +$53, T-30m -$14); 5 of 81 families have 95% LB > 0: wti-15m +$29/day on 38 events, nvda, tsla, whitehouse, rklb daily each < $3/day | P-019 (claude/project-thread-o5rbz8 pipeline/R036) | Only wti-15m is worth a node; P127r records wti, tsla, rklb. nvda and whitehouse not recorded (< $3/day each; add at next P127r restart, L11) |
| I-41 | 22 Nov | No decision-time book existed for any late-resolving cell; hindsight ceiling $868/day is 74% four 15-min commodity series with 1-2 days of tapes | P-019 | Resolving-books recorder P127r (live since 24 Nov 10:29Z); P148 forward score |
| I-42 | 23 Nov | MECE buy-all-NO smoke test: cheapest set 0.9945 before fees | DISCARDED-AUDIT | P133 recorder live; P146 scorer run |
| I-43 | 24 Nov | Perp catch-up on SPY up/down: +0.84c/share (run A, 5 trades) and +0.61c/share (run B, 5) at the 0.05 fee; depth at entry 5-80 shares | perps thread logs 24 Nov | Size, not sign, limits it; own live log 13:20-17:15Z today; P149 checks the cron |
| I-44 | 22 Nov | Daily up/down nowcast edge +3.4c +- 1.4c but measured depth $32/decision | REAUDIT | Parked capacity-limited |
| I-45 | 24 Nov | Weekend perps post-open drift +35 bp net (CI -22 to +96, 13 weekends); copper held-out +87 bp (CI +7.8 to +183, n 9, post hoc) | perps thread | P138 recorder Sun 29 Nov 22:00Z |
| I-46 | 22 Nov | Macro pickoff old FLOOR 4-19% of $200 on prints, 41% from one FOMC day | SPEC-macro-pickoff-paper-2026-11-24 | PCE recorder P135b 25 Nov; score after 13:30Z |
| I-47 | 24 Nov | ATP pre-flight passed (7 markets, 14 tokens, 1,798 rows/60 s) but tennis was tied to the soccer gate | P139a | ATP keeper split out as P139c (IT-OPS 0400Z) |
| I-48 | 24 Nov | P127r series appear only when their markets list: TSLA/RKLB after 20:31Z, post-counts by 16:56Z | P127r report | Health reads time-gated to listing times |
