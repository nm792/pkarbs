# How rn1 made its money, 22-29 Oct 2026 (fill-by-fill, 3 Nov 2026)

Wallet 0x2005d16a84ceefa912d4e380cd32e7ff827875ea. Every one of its 72,744 fills in the window (all buys, $17.95M), with all markets now resolved except $1.3k.

## Method (exact identity, no model)
For each fill (shares s, price paid p, result payout P = 0 or 1, Polymarket's 1-minute price series m(t) for that outcome):

    s*(P - p) = s*(m0 - p)        entry: price paid vs the market price at the fill
              + s*(m60 - m0)      first minute: market move in the 60 s after the fill
              + s*(m600 - m60)    1-10 min move
              + s*(P - m600)      hold: holding from 10 min to the result

The four parts always sum to the fill's trade P&L. Fees per fill are from on-chain OrderFilled word 4 (sum $49,592, equal to the activity feed). Rebates and rewards are the activity rows paid in the window (account level, not per fill).

## Result: net +$372k = four parts (MEASURED)

| Part | $ bought | Trade P&L | Fees | Net |
|---|---|---|---|---|
| A. CS2 taker buys (it crosses the spread) | 0.89M | +186.8k | -20.8k | **+166.0k** |
| B. Maker fills, all sports (its resting bids get hit) | 15.44M | +212.8k | 0 | **+212.8k** |
| C. Taker buys, other sports | 1.62M | -59.5k | -28.8k | **-88.3k** |
| D. Rebates and rewards (maker 41.3k, taker 24.9k, rewards 15.4k) | | | | **+81.7k** |
| **Total** | 17.95M | +340.1k | -49.6k | **+372.2k** |

### B. Maker fills by component (MEASURED vs the price series)
| | Entry (bought below market) | First minute | 1-10 min | Hold | Trade P&L |
|---|---|---|---|---|---|
| All maker | +413.7k (2.7%) | -166.1k | +5.7k | -40.5k | +212.8k (1.4%) |
| Soccer and other | +178.4k | -68.2k | +31.5k | +28.1k | +169.8k |
| CS2 | +75.6k | -26.7k | +3.1k | +1.9k | +53.8k |
| Tennis | +130.9k | -59.0k | -2.3k | -34.2k | +35.4k |
| US sports | +26.9k | -10.7k | -26.1k | -31.6k | -41.5k |
| Other esports | +1.9k | -1.4k | -0.6k | -4.6k | -4.7k |

Reading: it earns the bid-ask spread (about 2.7% of dollars at entry), loses about 40% of that within a minute to traders who know more (the price moves against its fresh fills), and the rest roughly washes out by the result.

### A. CS2 taker buys (MEASURED)
| | Entry | First minute | 1-10 min | Hold | Trade P&L |
|---|---|---|---|---|---|
| CS2 taker | -23.1k | +41.5k | +30.1k | +138.3k | +186.8k (21%) |

By market type (cs2detail.json):
- Map winner: $400k, avg price 0.467, won 0.594 per share, +$109k (+27%), 54 events, 34 positive, 90% event-bootstrap +42k to +184k.
- Match winner: $398k, price 0.439, won 0.493, +$49k (+12%), interval -38k to +134k.
- Other (handicaps, totals): $89k, +$29k, interval -11k to +77k.

All CS2 taker buys together: 90% interval +69k to +312k over 56 events. **This is the only cell of the eight sport-by-role cells whose interval excludes zero** (boot.json).

Reading: when rn1 crosses the spread in CS2 it buys sides that the market prices at 47c and that win 59% of the time. Only about a third of the gain shows up in the price within 10 minutes; most is realised at the result. So it is predicting CS2 outcomes better than the market, not only reacting faster. Taker buying in other sports loses money after fees.

### Share of net profit
CS2 taker 45%, maker spread (all sports) 57%, other taker -24%, rebates and rewards 22%.

## CS2 since 29 Oct (MEASURED, activity feed)
rn1's daily CS2 buying: 29 Oct $660k, 30 Oct $363k, 31 Oct $266k, 1 Nov $18k, 2 Nov $0, 3 Nov to 03:15Z $0. Polymarket did list the 2 Nov CS2 games with big volume (FURIA-FaZe $2.40M, MOUZ-TYLOO $0.73M). So there are no rn1 CS2 fills to match to our live round scores yet; its biggest profit source has been off for two days.

## What is not settled
- The price series is CLOB prices-history at 1-minute points. Not confirmed whether it is the mid or last trade. Changes the split between entry and first minute, not the totals.
- One week only (56 CS2 events). Out-of-sample check on 29 Oct-1 Nov is next.
- Why the CS2 taker buys win (a faster data feed, a better model, or both) is not measured. Needs round-by-round score history for 22-31 Oct matched to its fill times.
- calib.json (time-weighted price vs result by price band) has strongly correlated points within each market, so it is not used for conclusions.
- The 29 Oct a4.py figure (+$296k) used the 29 Oct snapshot when 279 markets were still open; with all resolved it is +$340k.

## Files
Repo rn1/decomp/: scripts/decomp.py, cs2detail.py, boot.py, calib.py, pull_activity.py; out/*.json; raw/ (activity 29 Oct-3 Nov, refreshed market metadata).
Price series for all 15,184 outcome tokens: /mnt/project-files/rn1/raw/prices/clob_all_2026-10-22_29.tar.gz (219 MB, too big for git). Fill inputs: /mnt/project-files/rn1/raw/act7d.json.gz, trades7d.tar.gz, onchain_orderfilled.tar.gz.

Confidence 7/10 (see "What is not settled").
