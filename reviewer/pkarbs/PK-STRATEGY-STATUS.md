# PK arbs: every strategy x status (Reviewer, 25 Nov 2026 01:25Z = 09:25 HKT)

Goal: $200/day for PK (Nick). Paper only; nothing traded or staged. Each row stands alone (no pooled averages).
Sources read at 01:20Z: pkarbs `reviewer` 18753603f5 (INBOX/OUTBOX, OPEN-ITEMS, DISCARDED-AUDIT, prototypes), trading-test `dialogue` 1f2e6b6cd (OPEN.md, OPEN-DONE.md, NEEDS-NICK.md, from_agent/pkarbs/*).

**Headline facts**
- PK proven $/day: **$0**. No strategy has a scored live-paper result.
- **The IT P lane has taken no PK row since 24 Nov 20:54Z** (PASS-P.tsv: "idle: no open P rows" every 30 min). Every P row is `waiting`. Most data is being recorded; nothing is being scored. That is the main reason nothing moves.
- **PK owner threads silent since 24 Nov 15:25Z** (last INBOX row P-PS-042). Under the standing rule the Reviewer does the work itself from here.
- Two corrections to the 24 Nov list: the **macro spec exists** (pkarbs reviewer SPEC-macro-pickoff-paper-2026-11-24.md, cc8d64e0b5, 24 Nov 02:59Z), and the **copper recorder request exists** (it/P-PERP-WKND-recorders-R086.md = IT row P138, start Sun 29 Nov 22:00Z).
- PandaScore capture is **not fully silent**: IT's P143 read at 15:20Z 24 Nov found raw files for 24 Nov 13Z, 14Z, 15Z (15Z = 8,400 B) from the old process. A test on those hours needs no approval.

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
| 9 | PandaScore CS2 kills lead | No valid result (old +0.83c gross, scorer bugs) | No | v4 capture fix (heartbeat, timeout, hour close) needs Nick's server-code yes (NEEDS-NICK since 15:25Z 24 Nov). Old process wrote 24 Nov 13-15Z hours | (a) Nick yes/no on v4; (b) IT runs P105 plant test on the 24 Nov 13-15Z hours now (read-only) | (a) Nick; (b) IT | (a) now; (b) next P run |
| 10 | CS2 taker (RN1 data edge) | RN1's own fills: taker +$115K on $956K (+12.0%, CI -$45K to +$287K, 73 matches); price moves his way +2.3c/30 s after his takes. Not our trades | No | Timing vs public events needs PandaScore capture on his take days (overlap 0 so far, P-PS-040) | Depends on #9; meanwhile list his CS2 take days from public fills and check overlap with the 24 Nov 13-15Z hours | Reviewer | after #9(b) |
| 11 | NBA maker (RN1-style post-only, spec v6) | Held-out: 1-min +3.74%, to-settlement **-11.5%** [-28.1, +5.2] on 39 games; RN1 NBA 3 days -0.7% | No; not shown positive | C2 live trade-feed probe P141 held by NEEDS-NICK-4; tonight's 00:12Z slot passed. P140 placement read: 33,308 of 33,503 RN1 fills had no recorded book (coverage gap) | Nick yes/no on P141 (read-only, stores nothing); Reviewer explains the P140 book gap | Nick; Reviewer | before 26 Nov 00:00Z tip-off |
| 12 | RN1 sports maker, soccer first (Ligue 1, Serie A) | RN1's fills, 30 days: maker L1 +4.5%, SA +3.8%, CIs span 0; without his best 5 markets negative in all leagues | No | No L1/SA game until Fri 27 Nov; soccer recorders P139b gated 27 Nov 11:00Z | Recorder start at first kickoff; maker spec ranked by edge per competing maker | IT (P139b); Reviewer spec | 27 Nov |
| 13 | Weekend perps drift + copper/metals Sunday reopen | Post-open drift +35 bp net (CI -22 to +96, 13 weekends); copper held-out +87 bp (CI +7.8 to +183, n 9, post hoc) | No | Calendar: next window Sun 29 Nov 22:00Z (P138) | Pre-flight 29 Nov 20:00Z; spec draft 28 Nov 12:00Z | IT; perps thread else Reviewer | 28-29 Nov |
| 14 | Dota (TheSports D1) | Never scored | No | Recorder P122b running since 23 Nov 17:24Z (health PASS); no scorer named | Write the scoring spec (lead vs own-token books, planted case) | Reviewer | 25 Nov |

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

## C. Waiting on Nick (server code or holds)
1. PandaScore capture v4 deploy (row 9). Default if no answer: no deploy, no PandaScore test beyond the old process's files.
2. P141 NBA trade-feed probe, read-only, stores nothing (row 11).

Confidence 7/10 that every fact is right, rows do not overlap, and A+B cover every PK strategy on file. To reach 9: the outputs of the IT reads filed now (P137 24 Nov output, P121/P133/P127r scores, Goalserve rerun), and the 08:00Z/12:00Z owner deliverables or the Reviewer's own versions.
