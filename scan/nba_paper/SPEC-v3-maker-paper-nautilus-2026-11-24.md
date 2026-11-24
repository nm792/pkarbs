# SPEC v3 (24 Nov 2026): Nautilus-native maker paper spec, NBA post-only bids on both tokens (R-077(B), R-078(1))

Extends SPEC v2 (5147f01e2e) and v1 (a983d811); rows 1-22 there still apply unless changed here. PAPER ONLY, no orders ever (SETTLED A7). Runs on Prime only (R-039). STATUS: SPEC ONLY. Every code row is NOT BUILT, so every row is UNCHECKED until another thread signs the rule-to-code table. Offline code needs nobody's approval; any server change is ONE NEEDS-NICK row (R-047).

$ LABELS used below: SIM = from the simulation, not measured. FLOOR = measured and print-capped, true value at least this. UPPER = book-implied, true value at most this. UNPROVEN = no measurement exists. Basis for the only $ figure in this spec: sim about $70/day (+$9.6/game x 7.2 games/day; 90% range -$0.4 to +$18.9/game), SIMULATION with trade-derived mids and a 5 s feed delay; label SIM/UNPROVEN, not a result.

## 1. SETTLED facts this spec depends on (cited, not restated from memory)
- A1 own-token books only; NO is never priced from YES. Both tokens are quoted and scored separately.
- A3 hold: the 250 ms taker hold is NOT used for sports; each market's own seconds_delay is read from CLOB /markets (R-065: 0 on 2 NBA games at 09:00Z 23 Nov, 1 s on soccer, NHL, tennis, CS2).
- A4 rebates: maker rebate per the market's feeSchedule, scored separately from P&L (tier values read from SETTLED A4 and the market field at run time, never hard-coded).
- A7 never trade or stage orders. A8 no hindsight (principle 8). A9 bar $200/day lower CI. R-034 no $/day without measured depth.

## 2. What "Nautilus-native" means here
Paper strategy is a Nautilus Trader Strategy run in BACKTEST/replay mode on recorded data, never a live execution client.
- Data: books.jsonl.gz rows from P106e (it/pm_sport_books.js, f5be71e7f3) are converted to Nautilus OrderBookDeltas / QuoteTicks per token (one Instrument per token, tick 0.001, min size 5 shares, price precision 3). Single host clock recv_ms is the event timestamp.
- Execution: a custom simulated venue (no real adapter). Orders are Nautilus LimitOrder with post_only=True; the venue model in fillsim.py decides fills (section 4). Latency model: submit-to-accept adds the market's seconds_delay plus the measured Nautilus order latency distribution (agent/outbox/nautilus-order-latency-2026-11-05.md: median 0.206 s, p90 1.281 s, n=30, 5 Nov; that sample is small, so it is a parameter with a sensitivity run at 0, median, p90).
- No live strategy code path exists: the strategy class takes only a replay data client; a unit test asserts that importing an execution client fails (row 34).

## 3. Quote rule (both tokens)
Per game, per token (YES and NO separately), at each decision time t:
1. Read the market's seconds_delay d from CLOB /markets at t (row 15). Read failure = skip and log, never default.
2. Snapshot = latest own-book row with recv_ms <= t (none within 5 s = no decision). Mid m = (best bid + best ask)/2 of that token only.
3. Post-only bid at p = floor(m x 0.975, 0.001); must be strictly below own best ask (else post-only reject, logged as a no-quote). Size = max(5 shares, floor($200 / p)) capped so notional <= $200; if 5 shares exceeds $200 skip. One resting bid per token per decision, life 10 s then cancel (the rule under test), then both-token independent re-quote at the next decision.
4. Decision times: Stage A (no event feed, G2) = random event-free times, 200 per game window (the BASELINE arm); Stage B (event feed exists) = at frame recv_ms of an NBA score event only, never at official time (row 1). Real arm minus baseline arm is the only edge number.
5. Order is eligible to fill from t + d + order latency; no fill counts before that.

## 4. Fill model without own-token prints (the G1 gap, stated honestly)
G1: P106e records book and price_change only; last_trade_price is DROPPED (pm_cs2_books.js applyMsg ignores it). So there are NO own-token trade prints on this data, and "fill only on trade-through at or past our price" cannot be observed directly. I cannot claim a measured fill rate from this data.
What the spec does instead (Stage A, all UPPER bounds, none quotable as $/day, R-034):
- Queue position: at join time the size ahead at our price level = displayed size at that level in the own book (rank by price; if our price is a new level, ahead = 0 and we are first).
- Trade-through proxy (UPPER): our bid fills when the own token's best ask is observed at or below our price (a taker has crossed through us), OR the best bid falls strictly below our price while our price level was previously the best (level wiped out). Both need the book to show it, so a trade that clears the level and is refilled inside one 10 s slim window is missed (understates) while a cancel that looks like a wipe is counted (overstates); net direction UPPER.
- Queue-consumption proxy (UPPER): size at our level decreasing is counted as trades only up to the decrease, cancels and trades not separable, so ahead-size reaches 0 earlier than in truth.
- Rule for reporting: fills labelled UPPER; fill rate, fills x edge and any $ derived are UPPER or UNPROVEN, never FLOOR.
Stage B (measured fills) needs one of: IT confirms pm_trades_capture.py writes NBA own-token prints (read-only check, no change), or last_trade_price handling is added to the recorder (server code = ONE NEEDS-NICK row; cost: about 10-20 MB/day disk, risk: keeper restart gap about 1 min; default if Nick does not answer: Stage A only, reported as UPPER). With prints the rule becomes the stated one: fill only on a print at or through our price, queue reduced only by prints at our level, 10 s window.

## 5. Scoring
- Markouts: 1-min and 10-min, both on the own token's best bid at fill time + 60 s and + 600 s (own book, not the other token), per fill and per game; settlement per game (held to result) reported separately.
- Fees: maker fee from the market feeSchedule field (0 expected), taker fee never paid (post-only). Rebate per the market's feeSchedule and A4 tier, reported on its own line, not netted into the edge number; if the field is absent the rebate is UNPROVEN and excluded.
- Placebo/baseline: row 20 (200 event-free times per game). Plant: raw rows where a known bid fills, recovery 95-105% (test_plant.py on rows, not on summaries). Label swap: swap YES/NO labels, the edge must vanish.
- Rows added: 23 Nautilus data conversion exact (round-trip test: deltas rebuild the recorded best bid/ask on every row); 24 quote both tokens independently (a YES-only book gives no NO decision); 25 5-share minimum and $200 cap enforced; 26 10-min markout; 27 rebate line; 28 latency sensitivity runs; 29 no-live-path import test. All NOT BUILT.

## 6. Sequential stop rules (pre-set, MODELLING-PRINCIPLES 13) and sizing (14)
Unit = game-day pair cluster (game as unit; both tokens of one game are one cluster, since they are mirror books).
- First 10 games: NO P&L viewed; only counts, queue size ahead, completeness (>= 99% of expected token snapshots, R-037 definition).
- At game 10: sigma = 1.5 x baseline-arm per-game sd, frozen in a committed file with its SHA before the real arm is read.
- Always-valid 95% interval on mean per-game (real minus baseline) markout, 10-min markout as the primary, 1-min as secondary. SUCCESS: lower bound > 0. FUTILITY: upper bound < 0. MAX SAMPLE: 60 game-days, then "inconclusive, ranked". Looks only at games 10, 20, 40 then every 20; no other peeking.
- Stage A numbers are UPPER, so SUCCESS on Stage A only means "worth building Stage B", never "edge confirmed".
- Capacity (principle 14): edge x fillable size. Fillable size per decision = min($200, measured depth at our price at decision time incl. size ahead); daily cap $2,000 (R-034). Report median and 10th percentile size ahead per game (row 22), and $ that could rest within the caps. Sizing: fractional Kelly at most (quarter-Kelly default for any future sizing statement), applied to the lower CI edge, never the point estimate; no sizing statement is made until a lower CI exists.
- A9: $200/day lower CI at 7.2 games/day needs about +$27.8/game lower bound. Sim +$9.6/game = about $70/day = 35% of $200 (SIM). Stand-alone: NO (35% of $200 if sim holds, UNPROVEN). Stack layer: YES, candidate. What settles it: measured own-token prints (Stage B), size ahead at our price from measured depth, a measured feed delay under 2 s (register B1), and 30+ games.

## 7. Recorder health (R-077(B))
Latest P106e health read: NOT AVAILABLE TO ME, UNVERIFIED. I have no server access. The Reviewer relayed that the keeper has been live since 23 Nov 08:58Z (PID 236052, 20/20 tokens); I have not seen the health output. Command for IT to paste: `bash nba_health.sh /mnt/HC_Volume_107257520/pkarbs/pmnba/2026-11-23 60` (it/nba_health.sh a4744a2b7a; prints HEALTH PASS/FAIL, pid, single-process check, tokens, gz growth over 60 s, disk free). Until pasted, no claim that the recorder is running (Nick 19 Nov rule).

## 8. What changed from v2
Both tokens quoted (v2 allowed either); Nautilus replay venue defined; 5-share minimum; 10-min markout added; rebate line; latency sensitivity; fill model without prints made explicit as UPPER; capacity and fractional Kelly stated; health read item.

Confidence 7/10. To reach 9: (a) IT pastes the health read and row counts per token for the last hour; (b) IT states whether pm_trades_capture.py writes NBA own-token prints; (c) the feeSchedule and A4 rebate tier values are read from one NBA market's Gamma/CLOB record; (d) another thread signs the rule-to-code table.
