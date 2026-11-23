# SPEC v2 (23 Nov 2026): NBA quote-only paper test on the LIVE P106e recorder data (R-070 C, R-065)

Supersedes the run-plan parts of SPEC-nba-paper-test-2026-11-22.md (a983d811); rows 1-14 there still apply unless changed below. Paper only, no orders. Runs on Prime only (R-039), offline code needs nobody's approval; any server change needs Nick via ONE NEEDS-NICK row (R-047). STATUS: spec only, every code row NOT BUILT, so UNCHECKED.

## 1. What the live data is (read from code f5be71e7f3, not from the server)
P106e = it/pm_sport_books.js, NBA mode, 20 of 20 tokens since 08:58Z (reported by the Reviewer, R-070). Per token it writes into books.jsonl.gz: recv_ms (one host clock), asset (that token's own id), outcome, best bid/ask and the top 3 levels (price, size); level 2-3 changes are written at most once per 10 s per token, best bid/ask changes always (pm_cs2_books.js SLIM rule). markets.jsonl gives start time and tokens per game.

## 2. Gaps that decide what can be tested now
- G1 NO TRADE PRINTS. The recorder handles only book and price_change messages; last_trade_price events are dropped. So 'own-token trade-through' cannot be scored from prints yet. Stage A (now) uses BOOK-IMPLIED fills: our bid at price p fills when the own token's best ask falls to <= p (a crossed/taker-hit proxy), reported as an UPPER bound, and queue fill when size at our level is consumed according to size decreases (cancels and trades are not separable: UPPER bound). Stage B needs prints: a code change to the recorder (server code, so NEEDS-NICK) or the existing trades capture (pm_trades_capture.py) if IT confirms it runs for NBA tokens. Until Stage B exists no fill count is a result, only an upper bound.
- G2 NO EVENT TIMES. The Polymarket sports-WS NBA frames and the NBA liveData play-by-play are not recorded by P106e (cs2-logger-nba conditional per P-NBA-5, unverified). Without them the rule's trigger (a score event at WS receipt) cannot be replayed. Stage A therefore runs only the event-free baseline (section 4), to fix costs, queue size and placebo; the event test starts when a frame log with NBA rows and recv_ns on this host exists.

## 3. Per-market hold from CLOB (R-065)
For every token the harness reads that market's own seconds_delay from CLOB /markets at decision time and stores it in the decision row. Our order becomes eligible to fill at decision time + seconds_delay; fills before that do not count. R-065's 09:00Z read: 0 on 2 NBA games, so today the NBA hold is 0 s, but it is read, never assumed (rule row 15). SETTLED A3's 250 ms is NOT used for sports. If the read fails the decision is skipped and logged, not defaulted.

## 4. Test design (rule-to-code additions; all NOT BUILT)
| # | Rule | Code | Status |
|---|---|---|---|
| 15 | seconds_delay read per market at decision time, stored, used as the hold | nba_paper/delay.py | NOT BUILT |
| 16 | Decision uses only rows with recv_ms <= decision time; the base mid is the own token's best bid/ask mid, YES and NO separate | decide.py | NOT BUILT |
| 17 | Quote: post-only bid = floor(mid x 0.975, 0.001); size <= $200; one resting bid per token and event, 10 s life, then cancelled (as in the rule under test) | decide.py | NOT BUILT |
| 18 | Stage A fills = book-implied upper bounds (best ask <= our price; size consumed at our level); fills labelled UPPER; Stage B fills from own-token prints, both reported | fillsim.py | NOT BUILT |
| 19 | Score: 1-minute markout on the own best bid at +60 s, plus settlement per game, fee from the market fee field (maker 0, rebate separate) | score.py | NOT BUILT |
| 20 | Baseline (event-free, runs now): same quote at 200 random event-free times per game window; real minus baseline is the only edge number; also gives the baseline queue size ahead at our price | score.py --baseline | NOT BUILT |
| 21 | Plant: raw book rows where a known cheap bid fills 95-105% of planted; label swap must kill the result | test_plant.py, test_labelswap.py | NOT BUILT |
| 22 | Capacity: size ahead at our price at decision time, median and 10th percentile per game; $ that could rest within the $200 and $2,000/day caps | fillsim.py | NOT BUILT |

## 5. Pre-set stop rules (frozen before any P&L is read)
- Unit = game. First 10 live games: NO P&L is looked at; only counts, queue size, data completeness (>= 99% of expected token snapshots, per R-037 definition).
- At game 10 the per-game sd of the markout is estimated from the baseline arm only (not the real arm), sigma is registered as 1.5 x that sd and frozen in a committed file with its SHA.
- Always-valid 95% interval on the mean per-game real-minus-baseline markout. SUCCESS: lower bound > 0. FUTILITY: upper bound < 0, or at 60 game-days with the interval still containing 0 -> 'inconclusive, ranked'. No peeking rule: results only at the pre-set checkpoints games 10, 20, 40, then every 20.
- A9 bar: $200/day lower CI. At 7.2 games/day, the lower bound must exceed about +$27.8/game. The old sim figure is +$9.6/game (about $70/day = 35% of $200, not measured), so a SUCCESS here is a stack layer, and the report must say stand-alone % of $200, stack-layer yes/no, and what would settle it.
- Any figure from Stage A is an UPPER bound and may not be quoted as $/day (R-034); only measured own-token depth at decision time (rule 22) plus Stage B prints produce a $/day.

## 6. What I need and who decides
1. IT: confirm whether pm_trades_capture.py (or the sports-WS logger) writes NBA own-token prints and NBA frames today; paste row counts for the last hour. (Row to be filed with the watcher.)
2. NEEDS-NICK (one row, only if the answer to 1 is no): add last_trade_price handling to the recorder (server code) and an NBA liveData poller. Cost: small (no new feed cost; disk about 10-20 MB/day more); risk: a restart of the keeper, so a gap of about 1 minute; default if Nick does not answer: keep Stage A only and report it as upper-bound.
3. Code order after approval-free items: baseline + plant + label-swap + delay.py first (offline, testable against the local fakes), then the event replay when G2 is closed.

Confidence 7/10 as a spec. To reach 9 I need the recorder's data checked on Prime (rows per token in the last hour) and IT's answer to item 1.
