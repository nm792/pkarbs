# Our fill simulation vs rn1's real maker fills (3 Nov 2026)

**Question.** Our bid backtests (LoL, soccer, NBA) all show the plain "bid at market - 2.5%" rule losing about 3-8% within 1 minute. But rn1's real maker fills in the same markets are profitable. Is the simulation wrong?

**Answer: yes, mostly.** The simulation counts fills that almost never happen to a real resting bid. With a corrected rule, the simulation lands within about 1 point of rn1's real results.

## Data (all measured)
- rn1's maker fills from 22 Oct 02Z to 29 Oct 02Z: activity rows minus the takerOnly set (raw/trades7d). Soccer 34,961, NBA 3,743, LoL 813.
- Full data-api v2 trade lists for those 6,316 markets, with transaction hashes (raw/fillcheck/trades). The list has one row per taker transaction. A maker fill does not get its own row; it sits inside the taker's row. A taker that sweeps several price levels shows up as one row at its average price.
- Scripts: fillcheck/pull.py, analyse.py (out_fillcheck.json), us/d_test.py, us/diag_nba.py, us/nba_guard_c.py, soccer/backtest.py with FILL_MAX_GAP.

## 1. What fills rn1 in reality (in-play)
| Sport | rn1 maker fills | $ | Bought below mid | 1-min markout | Filled by a trade AT rn1's price | Trade below rn1's price | Sweep, average above |
|---|---|---|---|---|---|---|---|
| Soccer | 29,081 | $5.48M | 1.57% | **+0.62%** | 92% | 2% | 5% |
| NBA | 1,655 | $0.10M | 0.96% | **-0.23%** | 87% | 8% | 5% |
| LoL | 783 | $0.06M | 1.83% | **-2.89%** | 82% | 11% | 7% |

Real fills come from sellers hitting the bid **at its own price**, because the resting bid is the best bid. Only 2-11% come from trades printing below the bid.

## 2. What the simulation fills on (NBA, plain rule, 78 games)
The fill rule was "a sell trade printing below our bid fills us at our bid". The market price is taken from recent trades.
| How far below our bid the trade printed | Share of fills | 1-min markout |
|---|---|---|
| under 1% | 17% | -0.8% |
| 1-3% | 23% | -2.2% |
| 3-10% | 34% | -5.8% |
| over 10% | 25% | **-22.8%** |

About 60% of simulated fills come from trades 3% or more below our bid, while rn1 almost never gets filled that way. A trade far below our bid means the order book had already moved, without trades, between two prints. The simulation only sees trades, so it leaves our bid at a stale price and gets it picked off. A real bot watches the book and would have moved its bid down first. These fills are mostly an artefact of having no order-book history, and they cause nearly all of the simulated loss.

Checked and ruled out (NBA, us/mid_test.py, us/d_test.py): how the "market price" is built from trades (pair of last trades within 120, 20 or 5 s, or last trade only) changes nothing (-7.2 to -7.6%). Bidding closer to market (0.25-5% under) still loses -5 to -9% under the old rule. Tick size is 0.001 in these markets, so rounding is not the cause.

## 3. Corrected fill rule
**A resting bid at b fills only on a sell trade that prints at or below b and within 1% of b** (max_gap = 0.01 in common.sim). Trades further below are treated as moments when a book-watching bot would already have re-pegged its bid. The 3% version is reported as a sensitivity check.

Validation against rn1's real fills (plain rule, no guards):
| Sport | Old simulation, 1 min | Corrected (1%), 1 min | rn1 real, 1 min |
|---|---|---|---|
| Soccer (328 matches, rebate included) | -7.9% | **-0.1%** [90% range -0.4, +0.2] | +0.6% (before rebate) |
| NBA (78 games, no rebate in NBA) | -7.2% | **-0.8%** [-1.0, -0.6] | -0.2% |

The remaining gap of 0.5-0.7 points is consistent with rn1 bidding about 1-1.5% under market (at the best bid) and choosing when to bid. We bid a fixed 2.5% under.

## 4. NBA with the corrected rule (guards pass test)
| Variant (1% rule) | $ filled | 1 min | To result [90% range by game] | To result, top 5 games removed |
|---|---|---|---|---|
| Plain | $625k | -0.8% | -1.1% [-4.5, +2.3] | -4.9% |
| Speed guard, 3 s feed | $358k | 0.0% | -2.7% [-7.8, +2.7] | -8.1% |
| Speed guard, 10 s feed | $440k | -0.7% | -1.9% [-6.0, +2.4] | -6.4% |
| Veto, 5-point edge | $210k | -0.3% | -11.5% [-22.7, +0.5] | -21.4% |
| Guard (3 s) + veto | $123k | +0.6% | -12.5% [-24.6, +0.3] | -22.4% |

**NBA still fails the pass test.** The model veto again loses to the market when they disagree. This agrees with rn1, which makes about 0 there and trades little.

## What this means for other threads
- The LoL backtests (bidsim/sim_bids.py, bt_gate.py, veto_timing.py) use the old rule. Their plain-rule -2.6% at 1 min and the size of any guard gain will change. They should be rerun with max_gap = 0.01 (and 0.03).
- The soccer guard results in winmodels/soccer/out_lag*.json also use the old rule; soccer work is stopped.
- For a real test, record order books (CLOB websocket book snapshots) during live games. Only that removes the artefact rather than trimming it.

Confidence 7/10. The 1% cutoff is fitted to match rn1's fill mix, not derived from book data. To reach 9: compare against a few days of recorded order books, and repeat with week-2 fills.
