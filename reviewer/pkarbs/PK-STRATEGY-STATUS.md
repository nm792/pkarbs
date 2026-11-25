# PK arbs: every strategy x status (Reviewer, 25 Nov 2026 01:25Z = 09:25 HKT)

Goal: $200/day for PK (Nick). Paper only; nothing traded or staged. Each row stands alone (no pooled averages).
Sources read at 01:20Z: pkarbs `reviewer` 18753603f5 (INBOX/OUTBOX, OPEN-ITEMS, DISCARDED-AUDIT, prototypes), trading-test `dialogue` 1f2e6b6cd (OPEN.md, OPEN-DONE.md, NEEDS-NICK.md, from_agent/pkarbs/*).

**All PK insights live in INSIGHTS.md (same folder); read it before any scoring run, spec or IT note.**

**Headline facts**
- PK proven $/day: **$0**. No strategy has a scored live-paper result.
- **The IT P lane has taken no PK row since 24 Nov 20:54Z** (PASS-P.tsv: "idle: no open P rows" every 30 min). Every P row is `waiting`. Most data is being recorded; nothing is being scored. That is the main reason nothing moves.
- **PK owner threads silent since 24 Nov 15:25Z** (last INBOX row P-PS-042). Under the standing rule the Reviewer does the work itself from here.
- Two corrections to the 24 Nov list: the **macro spec exists** (pkarbs reviewer SPEC-macro-pickoff-paper-2026-11-24.md, cc8d64e0b5, 24 Nov 02:59Z), and the **copper recorder request exists** (it/P-PERP-WKND-recorders-R086.md = IT row P138, start Sun 29 Nov 22:00Z).
- PandaScore 24 Nov 13Z/14Z raw files, events.jsonl.gz and pmcs2 markets files for those hours are now **MISSING** (P151, 02:50Z 25 Nov; present at 15:20Z 24 Nov). Only raw 22Z remains. P151 ran: tests ALL PASS, 0 matches, no result. Recovery from the live process's open handles filed IT-OPS 0305Z (P153, 65f08b22c). v4 deploy REFUSED 02:22Z: root 4.05 GB free < 5 GB floor, lock not held, events log missing; IT T117b moving 2 GB off root.

## A. Active strategies (each has a next step now)

| # | Strategy | $ and trades | Proven? | Exact blocker | Next action | Owner | When (UTC) |
|---|---|---|---|---|---|---|---|
| 1 | Perp catch-up on SPY up/down open contracts | 24 Nov live (cloud logs, 5 shares): run A 5 trades, **+0.84c/share** at the market's own 0.05 fee (3 of 5 positive); run B 5 trades, +0.61c/share (2 of 5). About $0.25-0.31 total. Depth at entry 5-80 shares | No. n=5 per run; ~hundreds of trades needed | Size: $20-80 at the touch. Prime cron P137 installed for 13:20Z weekdays but its 24 Nov 13:35Z health read was never filed (UNVERIFIED that it ran) | (a) IT read of P137's 24 Nov output; (b) Reviewer runs its own live logger again today 13:20-17:15Z and scores both; (c) Nautilus spec draft (perps thread, due today) | (a) IT via IT-OPS note; (b) Reviewer; (c) Reviewer if absent | (a) next P run; (b) 25 Nov 13:20-17:30Z; (c) 25 Nov 12:00Z |
| 2 | Mentions / "will X say Y" (whole class) | No measured $/day. Dell call 24 Nov: frozen 10c rule placed **no bet** (own asks never 10c under base rate; 18753603f5). Old print-sized FLOOR $4.9-13.3/day is not a result | No | P121 logger has recorded own-token books since 23 Nov 12:57Z (restarted on fixed code 24 Nov 09:26Z; health PASS 10:23Z, 162 tokens), but **no scorer has been run on them** | IT read-only run of the existing scorer on P121 books for events resolved 24-25 Nov (Thanksgiving pardon, Dell, others) | Reviewer files row; IT runs | row now; result by 25 Nov 12:00Z |
| 3 | Earnings-beat contracts (separate from will-say, Nick 03:56Z 24 Nov) | No result | No | Base rate (top-30, 12 quarters) was due 25 Nov 08:00Z from the mentions thread; thread silent | Reviewer builds the base rate from public data if not landed at 08:00Z | Mentions thread, else Reviewer | 25 Nov 08:00Z |
| 4 | MECE / neg-risk sets, buy every NO (3+ legs) | No result. Old smoke test: cheapest buy-all-NO 0.9945 before fees | No | P133 recorder live since 24 Nov 09:57Z (411 markets, 822 own NO+YES tokens, health PASS 10:58Z); **scorer it/mece_score.py (planted YES/NO PASS) never run on it** | IT read-only run of mece_score.py on P133 books 24 Nov 10Z to now | Reviewer files row; IT runs | row now; result by 12:00Z |
| 5 | Tweet / post count brackets | No result | No | P127r records elon-tweets, trump-truth-social, khamenei at leads 3h/1h/0.5h (confirmed 20:51Z); spec was due 25 Nov 12:00Z (signal-pipeline thread, silent) | Spec + first score of the recorded ladders | Signal-pipeline thread, else Reviewer | 25 Nov 12:00Z |
| 6 | Late-resolving wti-15m (+ tsla, rklb, nvda, whitehouse daily cells) | SCREEN only: wti-15m +$29/day on 38 events (lower bound >0), UNPROVEN | No | P127r live (PID 2777937) records WTI rows at 10/5/2-min leads; Nautilus spec v2 delivered (32c0aba01d); **no forward score** | IT read-only forward score of every WTI 15-min event recorded since 24 Nov 10:29Z | Reviewer files row; IT runs | row now; result by 12:00Z |
| 7 | Macro release pickoff (Core PCE) | No result. Old FLOOR 4-19% of $200 on prints (41% from one FOMC day) | No | P135a pre-flight PASS (24 Nov 03:30Z). P135b start is gated 25 Nov 10:00Z and must be running by 12:55Z, but the lane only takes rows marked `open`, so it can be skipped | IT flips P135b to `open` at 10:00Z; health reads 12:50/13:20/14:20Z; score after 13:30Z release | IT (note filed by Reviewer); score by Reviewer | 10:00-12:55Z; score 15:00Z |
| 8 | Goalserve lead (NHL, CS2; tennis) | NHL run 24 Nov 02-14Z: 5 matches = sizing block only, nothing scored (placebo_ok false at n=5). CS2: run stopped, pmcs2 hour 23 Nov 22Z missing | No | Needs 12 sizing matches before any test matches; CS2 window must avoid the 23 Nov 22Z gap. **Tennis has no Polymarket recorder** (P139a ATP pre-flight passed 05:24Z, recorder not started) | IT reruns v3 on NHL 24 Nov 02:00Z to latest full hour, and CS2 from 24 Nov 23:00Z | Reviewer files row; IT runs | row now |
| 9 | PandaScore CS2 kills lead | No valid result (old +0.83c gross, scorer bugs) | No | v4 approved (Nick 01:17Z) but start REFUSED 02:22Z: root 4.05 GB < 5 GB floor, events log missing. P151 plant run: 24 Nov 13-14Z inputs MISSING, no result | (a) P151c: hours FOUND on the box (P155); P151b found the tmp/P155 copy gone, so P151c pulls straight from the box into pkarbs/scratch and scores (IT-OPS 0735Z); (b) P143 deploy (preflight FAIL 04:xx: events log unreadable, old lock not held) | IT | (a) first P item; (b) next run |
| 10 | CS2 fast-data TAKER (RN1) - SETTLED as the concrete signal (Nick 24 Nov) | RN1's own fills: taker +$115K on $956K (+12.0%, CI -$45K..+$287K, 73 matches); price moves his way +2.3c/30 s, +2.8c/5 min after his takes. Maker side: no rule in CS2, Serie A or Ligue 1 (negative without top 5 markets). Not our trades | No | Timing test RAN 24 Nov 11:00Z: overlap 0 (no RN1 takes in captured matches). Rerun 25 Nov 01:30Z: 1 RN1 CS2 take since 24 Nov (12:29Z) vs PandaScore hours 13-15Z only: overlap 0 | PandaScore watchdog capture deploy (Nick yes 01:17Z), then daily rerun of rn1-cs2-timing during the PGL Major | IT deploy; Reviewer daily rerun | from deploy |
| 11 | NBA maker (RN1-style post-only, spec v6) | Held-out to-settlement -11.5% [-28.1, +5.2] on 39 games; RN1's own NBA about 0 EV (+0.19% on $4.1M) | n/a | **CLOSED by Nick** (project chat 24 Nov 09:50Z, cmsg_013Uyk4Z71q532SC6wKjVkyhBJaM8ebBByG5qVGhbADkym): NBA node dropped; P141 probe not needed | None. P106e recorder stays only as data; never ask Nick about NBA again | n/a | n/a |
| 12 | RN1-style soccer (Ligue 1, Serie A): maker side has NO copyable rule (settled, section H); taker side small (SA +$15.8K on $151K; L1 -$0.5K) | RN1's fills, 30 days: maker L1 +4.5%, SA +3.8%, CIs span 0; without his best 5 markets negative in all leagues | No | No L1/SA game until Fri 27 Nov; soccer recorders P139b gated 27 Nov 11:00Z | Recorder start at first kickoff; maker spec ranked by edge per competing maker | IT (P139b); Reviewer spec | 27 Nov |
| 13 | Weekend perps drift + copper/metals Sunday reopen | Post-open drift +35 bp net (CI -22 to +96, 13 weekends); copper held-out +87 bp (CI +7.8 to +183, n 9, post hoc) | No | Calendar: next window Sun 29 Nov 22:00Z (P138) | Pre-flight 29 Nov 20:00Z; spec draft 28 Nov 12:00Z | IT; perps thread else Reviewer | 28-29 Nov |
| 14 | Dota (TheSports D1) | Never scored | No | Recorder P122b running since 23 Nov 17:24Z (health PASS); no scorer named | Write the scoring spec (lead vs own-token books, planted case) | Reviewer | 25 Nov |

## SETTLED (Nick)
- S1 (24 Nov 09:50Z, project chat cmsg_013Uyk4Z71q532SC6wKjVkyhBJaM8ebBByG5qVGhbADkym and follow-ups): NBA maker node DROPPED, because RN1's own NBA is about 0 EV (+0.19% on $4.1M). P141 not needed. PK maker work moves to CS2 and soccer (Ligue 1 + Serie A), and the order is "keep probing until we find something concrete" (Nick 10:04Z). Don't re-test this or ask Nick about it again.
- Correction: the 01:25Z version of this table listed P141 as waiting on Nick. That was wrong, a repeat of a settled question.

## B. Parked, capacity-limited or closed (kept; nothing dropped)

| Strategy | State | Why | Reopens on |
|---|---|---|---|
| Gas daily (Polymarket, Kalshi) | Off | Nick 22 Nov 05:22Z "forget about gasoline" | Nick |
| Daily Up/Down nowcast | Capacity-limited | Edge +3.4c +- 1.4c but measured depth $32/decision | Deeper books |
| Perp vs PM SPX open | Capacity-limited | ~$1.4K/day volume; FLOOR $5.3/day | Volume |
| Chess in-play | Capacity-limited | <$2K/day volume | Volume |
| Mirror pairs | Parked with MFW | Scored on midpoints, no valid verdict | Nick |
| OddsPapi / Pinnacle lead | Open, low | 1-2 s lead inside the 1 s sports delay | Finer windows |
| Rugby, tennis books | Untested | Tennis NO never recorded; 6 Nations gate 30 Nov | 30 Nov |
| After-hours gaps / NVDA perps legs | Untested | No test on file | Logger data |
| Forecast edges (Netflix, MrBeast, box office), golden method | Open for re-audit | Print-only nulls | Depth-measured test |
| Own CS2 model, Kalshi index leader, sports MECE YES, 2-way MECE NHL/CS2, qlib/SPY lags | Dead on tests that could pass | See DISCARDED-AUDIT B | n/a |
| Up/down rebate MM | Moved to MFW | Nick 22 Nov 05:22Z | n/a |

## C. Waiting on Nick
Nothing. PandaScore watchdog capture: Nick YES, card 25 Nov 01:17:07Z, released to IT (trading-test reviewer IT-OPS-2026-11-25-0125Z, ce801255d). P141 NBA probe: removed from this list (Nick 01:17Z: already discussed); stays unrun.

## TOP PRIORITY (Nick 01:29Z 25 Nov): a valid lead/lag measurement for each TRIAL feed vs Polymarket own books, scored daily
| Feed | Exact blocker | Clear it by (UTC) | Then daily |
|---|---|---|---|
| PandaScore | Capture v4+watchdog not yet live (Nick yes 01:17:07Z; IT P143 released, ce801255d). The swap needs a gap with no live CS2/Dota socket, and the PGL Major is running | Deploy in the first gap today; heartbeat health read 15 min later | IT standing row P152: every day 06:00Z, P105 plant run on each complete hour with CS2 books from the day before; result appended |
| Goalserve NHL | 5 of 12 sizing matches at 14:00Z 24 Nov; placebo not OK at n=5 | P150 rerun after 25 Nov 06:00Z, which includes the 24-25 Nov night slate; expect sizing complete, test matches from the 25-26 Nov slate | P152 runs v3 NHL daily 06:00Z, cumulative window from 24 Nov 01:56Z |
| Goalserve CS2 | pmcs2 hour 2026112322 missing stops the run | P150 from 23 Nov 23:00Z | Same P152 row, CS2 cell |

## D. FULL LEDGER: every PK item ever raised, each with a next action and a time (25 Nov 01:45Z)
Sources merged: the 14 rows of section A; OPEN-ITEMS.md rows 1-27; DISCARDED-AUDIT-2026-11-23.md A (reopen ranks 1-14) and B (every stays-dead row); trading-test REGISTER.md P1-P21. Owner is the Reviewer unless named. Times are UTC. A row leaves only on Nick's word or a test that could pass.

| L | Item (source) | State now | Next action | When |
|---|---|---|---|---|
| L1 | Perp catch-up, SPY open contracts (A1) | 5 trades +0.84c/share; capacity $20-80 | IT P149 read; own live log + score | 25 Nov 13:20-17:30 |
| L2 | Mentions frozen 10c rule, all families (A2; OI 1-2; Reg P1) | P121 books unscored | IT P147 score; rescore in cloud | 12:00 |
| L3 | Mentions transcript base rate (OI 23; Reg P2) | Design 9138be8025, untested; Dell n=3 done (no bet) | Build the per-word transcript base rate for every open earnings-call word market from public transcripts, then check own asks | 25 Nov 10:00 |
| L4 | Mentions live speech nowcast (OI 24; Reg P2) | Design only; frozen-fair during-event -$78.93/day is not a test of it | Specify hazard model and caption source; planted case at 250 ms | 26 Nov 06:00 |
| L5 | Mentions count-market pooling defect (OI 25) | Fix flag + 5 tests delivered 23 Nov (effect -2%) | Confirm the deployed P121 scorer sha 5e44c570 carries the flag | 25 Nov 03:00 |
| L6 | Mentions firelog P103 (Reg P17) | CLOSED 25 Nov 07:40Z: superseded by the P121 WS paper logger, which records every decision with own-token asks (decisions.jsonl); P147 scores it | none | closed |
| L7 | Earnings-beat contracts (A3; OI 26; Reg P10) | Recorder tags family=earnings_beat; base rate due 08:00 | Base rate if not landed | 08:00 |
| L8 | MECE buy-all-NO, 3+ legs (A4; OI 4; Reg P3) | P133 recording, unscored | IT P146; also find or declare lost the 17 Nov probe files | 12:00 |
| L9 | Tweet / post counts incl. Trump (A5; OI 3; Reg P4) | P127r recording; Trump count used wrong source (6 of 63) | IT P148 rows; spec + first score | 12:00 |
| L10 | Late-resolving wti-15m (A6; OI 6; Reg P7) | Screen +$29/day; recording | Forward score from P148 rows | 12:00 |
| L11 | Late-resolving: other 4 families with 95% LB>0 of 81 (OI 6) | Only wti-15m and 4 stock dailies are recorded | List the other families from b33db0ee66 and add them to the P127r series file (IT row) | 25 Nov 06:00 |
| L12 | Macro pickoff, Core PCE (A7; Reg P6) | P135b start gated 10:00 | IT flips P135b; score after release | 10:00-15:00 |
| L13 | Goalserve lead NHL/CS2 (A8; OI 11; Reg P16) | NHL 5 of 12 sizing matches | IT P150 rerun | next P run |
| L14 | Tennis: Goalserve tennis, TheSports T1 maker (OI 9, 14) | No tennis PM recorder; T1 taker closed, maker untested | IT row to start the ATP keeper (P139a pre-flight PASS 05:24Z 24 Nov) | 25 Nov 06:00 |
| L15 | PandaScore kills lead (A9; OI 10; Reg P11) | Approved 01:17Z; deploy refused (root < 5 GB); P151 inputs missing | P153 recovery; P143 after T117b | next P run |
| L16 | CS2 fast-data taker / GRID (A10; settled) | Nick 01:29Z: he is handling the feed question himself; no new feeds until the trial feeds are timed | None from the Reviewer; do not raise | Nick |
| L17 | RN1 soccer L1/SA (A12; settled maker no rule) | Recorders gated 27 Nov | Taker-side probe on soccer like CS2 section H, from public fills | 25 Nov 09:00 |
| L18 | NBA maker (A11) | CLOSED by Nick 24 Nov 09:50Z | none | - |
| L19 | Weekend perps drift (A13; OI 7; Reg P8) | P138 gated 29 Nov | Pre-flight 29 Nov 20:00; spec 28 Nov 12:00 | 28-29 Nov |
| L20 | Copper/metals Sunday reopen (A13; OI 15; Reg P9) | Forward shadow; first read 31 Jan 2027 | Rides P138 | 29 Nov |
| L21 | After-hours gaps / NVDA perps legs (OI 27; Reg P12) | Rule lock was due 24 Nov 12:00, not found | Write the locked rule (pre-registered, planted case) | 25 Nov 09:00 |
| L22 | Dota / TheSports D1 (A14; Reg P15) | P122b live since 23 Nov 17:24 | Scoring spec | 25 Nov 11:00 |
| L23 | TheSports NBA delay, LoL, cricket box files (OI 9; Reg P14) | 39/40 Dota games, 885 NBA games captured; P124 list pending | Ask IT for the P124 manifest status; score LoL/cricket offline | 25 Nov 06:00 |
| L24 | NHL / rugby (OI 14; Reg P13) | NHL in L13; rugby 6 Nations gate 30 Nov | Rugby recorder note | 29 Nov |
| L25 | Re-audit final table (OI 5; Reg P18) | CLOSED 25 Nov 07:40Z: replaced by DISCARDED-AUDIT-2026-11-23 + this ledger + INSIGHTS.md | none | closed |
| L26 | Golden method on less-crowded rule-settled series (OI 16; Reg P19) | Untested beyond gas | Pick 3 candidate series with rule-settled statistics and list their volumes | 26 Nov 06:00 |
| L27 | Forecast edges: Netflix, MrBeast, box office, Kalshi index leader (OI 19) | Print-only nulls; Kalshi leader dead (-17c to -29c) | Depth check on the next listing of each | 26 Nov 12:00 |
| L28 | Daily Up/Down nowcast (DA B) | Capacity-limited, depth $32 | Re-measure depth once a week | 1 Dec |
| L29 | Perp vs PM SPX open (DA B) | Capacity-limited, about $1.4K/day | Folded into L1 | - |
| L30 | Chess in-play (DA B) | Capacity-limited, under $2K/day | Volume check | 1 Dec |
| L31 | Mirror pairs (DA B) | Parked with MFW; midpoint-scored | Own-ask rescore if Nick reopens | Nick |
| L32 | Intra-game maker / pre-kickoff rewards (DA B) | Closed by Nick; reward terms may have changed since 24 Oct | Read the current rewards terms and report any change | 25 Nov 12:00 |
| L33 | Funding-window reversion at 0.9 bp (DA B) | Dead; 1x-spread sensitivity never printed | Print the 1x sensitivity | 26 Nov |
| L34 | Midterm cross-venue MECE (DA B) | One-off, about $2.1K | none | - |
| L35 | Gas daily (OI 17; Reg P20) | Off by Nick | none | - |
| L36 | OddsPapi / Pinnacle lead (OI 13; Reg P21) | Closed, inside 1 s delay | none | - |
| L37 | Own CS2 win model, sports MECE YES, 2-way MECE NHL/CS2, tennis taker, overshoot, qlib/SPY lags (OI 12; DA B) | Dead on tests that could pass | none | - |
| L38 | Up/down rebate MM (OI 20) | Moved to MFW | none | - |

Confidence 7/10 that every fact is right, rows do not overlap, and A+B cover every PK strategy on file. To reach 9: the outputs of the IT reads filed now (P137 24 Nov output, P121/P133/P127r scores, Goalserve rerun), and the 08:00Z/12:00Z owner deliverables or the Reviewer's own versions.
