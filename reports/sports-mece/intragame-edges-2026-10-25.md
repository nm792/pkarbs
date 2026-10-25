# Intra-game edges beyond set arbs (25 Oct 2026)

Question (Nick): after a goal the cheap leg moves away from us; are there other edges inside a game?

Short answer: on 80 liquid soccer games, the taker-side ideas (drift, overshoot, stale legs) show
nothing we can reach once the 1 s sports delay is applied. The only idea the data does not rule out is
the maker side: resting quotes earned about zero in quiet periods and lost only around goals, and the
delay is exactly what lets a maker cancel before a goal hits them. That needs book data to test, so it
is the one server job proposed below. Confidence 7/10.

## Data and labels

- **Sample:** the 80 highest-volume closed soccer negRisk 3-leg games (Win/Draw/Win) on gamma with
  kickoff 18-23 Oct 2026, every taker trade per leg from `data-api.polymarket.com/trades`
  (84,041 trades, 58,008 in play, no leg hit the 10,000-offset cap). All 240 legs have `secondsDelay=1`.
- **Shocks:** 183 goal-like shocks in 69 games: a leg trades at least 10c away from its median of the
  previous 150-20 s, confirmed by a second trade within 15 s, one per game per 10 minutes. No look-ahead.
- **Prices** are YES-equivalent last trades (NO at q = YES at 1-q). Timestamps are whole seconds and
  already include the 1 s delay. There are no books or mids in this data.
- **Every number below is computed on real public trade prints**, but "edge" figures that use a later
  price as fair value are **estimates** of what was available, not a sim of what we would have filled.
- SEs are clustered by game. Script: `shadow/intragame_trades.py` (rerun gives the same numbers).

## Step 1: candidate edges (MECE by how we trade and against whom)

| # | Edge | How it would pay | What tests it | Tested here? |
|---|---|---|---|---|
| A1 | Post-goal drift (momentum) | Buy the jumping leg after the jump, price keeps going | Leg prices 10 s-10 min after a reachable entry | Yes |
| A2 | Overshoot reversal | Fade the jump | Same series, opposite sign | Yes |
| B | Stale-leg lag | Take quotes on any leg still at the pre-goal price | Stale trades by second after the shock, vs the 1 s delay | Yes (trade level) |
| C1 | Maker spread capture, cancel on shock | Rest at the touch in quiet play, earn spread + 15% maker rebate (+ rewards on EPL), pull quotes inside the 1 s delay | Markouts vs mid, queue position, cancel timing | Partly (no mids, no queue) |
| C2 | Maker first at the new level after a shock | Re-quote first after repricing, catch late takers | Post-shock book depth and fills | No (needs books) |
| D | Related markets in the same game | Moneyline vs totals / exact score / halftime lag after a goal | Prints on the related markets | No |
| E | Complete-set arb | Existing work | Owned by the "Verify clean rescan result" thread | Not repeated |

## Step 2: results

### A1/A2. Drift after a reachable entry: none (183 shocks, 69 games)
Entry is the first trade at least 1 s after confirmation (median 6 s after the first jump trade).
Move in the jump direction, per share:

| Horizon | Mean | SE |
|---|---|---|
| 10 s | -0.75c | 0.37c |
| 30 s | +0.42c | 0.51c |
| 60 s | +0.14c | 0.55c |
| 5 min | +0.50c | 0.91c |
| 10 min | -0.14c | 1.43c |
| to resolution | -2.7c | 2.7c |

All are inside noise and below a taker's cost (spread plus a 0.05·p(1-p) fee, about 1-2c). The -0.75c
at 10 s is the size of bid-ask bounce, so it is not an overshoot to fade.
Trap worth knowing: my first version required the price to *stay* moved 60-180 s later, which is
look-ahead, and it showed a false +4.2c at 5 min. Removing that filter removes the drift.
Sub-split, found after looking so treat as a lead only: jumps under 20c drift +2.0c (SE 0.9c, 111
shocks, 57 games) at 5 min; jumps of 20c or more drift -1.9c (SE 2.1c, 72 shocks, 45 games).

### B. Stale-leg lag: the pool is in the first second, which the delay hands to someone else
Trades that took a quote still at least 60% of the way back to the pre-goal price, legs that moved 5c+,
valued at the 60-180 s median after a 0.05·p(1-p) fee (estimate, ex-post fair value):

| Seconds after first jump trade | Other legs $ (shocks) | Jumping leg $ (shocks) |
|---|---|---|
| 0-1 | 4,436 (32) | 12,712 (25) |
| 2 | 100 (5) | 141 (2) |
| 3-5 | 886 (4) | 51 (2) |
| 6-10 | 885 (6) | 88 (3) |
| 11-30 | 98 (5) | 154 (3) |

About $17.1k was picked off in the first second and about $2.4k after it, over 80 games in six days.
A bot reacting to the feed submits after it sees the first jump print, so its order matches at
t+1 s or later: only the $2.4k is in reach, it sits in about a dozen shocks, and two shocks
(Cambuur v AZ is one) are most of it. That is roughly $400/day before competition, and someone already
took all of it at the time. **Not a robust edge.** It matches the set-arb finding: the legs we miss are
the ones already repriced.

### C1. Maker markouts: zero in quiet play, losses only around shocks
What the resting side of each in-play trade earned, per share, against the YES last trade later:

| Period | Trades | Shares | 60 s (share-wtd / trade mean ± SE) | 5 min | To resolution (trade mean ± SE) |
|---|---|---|---|---|---|
| Quiet (not within -5..+60 s of a shock) | 51,171 | 22.6M | -0.02c / +0.15c ± 0.13c | -0.01c / +0.10c ± 0.22c | -0.9c ± 0.6c |
| Near a shock | 6,837 | 1.3M | -2.4c / -0.3c ± 0.3c | -5.7c / -0.5c ± 0.6c | -0.9c ± 1.3c |

Read: in quiet play, liquidity at the touch roughly broke even before rebates. Around shocks, makers
lost about 2.4c per share at 60 s, mostly on large fills. A maker who is out of the book when shocks
hit, and who collects the maker rebate (about 0.0075·p(1-p), so about 0.2c at p=0.5, estimated) is
the one structure here with a plausible positive sign. This data cannot say whether our quotes would
be filled (queue position) or how fast we can cancel, and last-trade markouts include bid-ask bounce.
So C1 is **open, not shown**.

## Step 3: one proposed server job (not pushed; it waits behind the open 02Z task)

**Question:** in one hour of data-v2 books, does a quote that joins the back of the queue at the best
bid or ask in quiet play, and is cancelled when any leg of that game moves, make money net of
markout to mid at 10 s and 60 s, after adding the maker rebate?

- **Local first:** a maker sim in `shadow/` on top of `books.Replay` (queue ahead = displayed size at our
  price when we join; we fill only after trades at our price consume it; cancel after 200 ms from the
  first price_change of 3c+ on any leg), with synthetic books whose fills and markouts are hand-computed,
  added to `test_gates.py`.
- **Gates (fail = no P&L):** mid at each run equals the exchange best_bid/best_ask midpoint (G5 style);
  every simulated fill has a real trade print at our price at or after our queue is cleared.
- **Pass/fail for the edge, fixed now:** PASS if mean (markout to mid at 60 s + rebate) per share is
  above zero by more than 2 game-clustered SEs, over at least 15 games and 200 fills; otherwise FAIL.
- **Bounds:** one hour (02Z, already gated), one process, `systemd-run MemoryMax=1500M`, `timeout 1800`, cleanup and `ps`/`free -m` after.

Not proposed: more logging or new hours. D (related markets) can be tested later from public prints
the same way as above without the server.

## Addendum (07:30Z): maker upper bound, and the server job is withdrawn

Nick asked why simulate a break-even maker. Upper bound from the same public prints instead
(computed on real prints unless marked estimate; 80 games over 6.04 days):

- In-play volume: 3.74M shares/day in quiet play, 0.22M/day within -5..+60 s of a shock (5.8%).
- Effective spread is 1 tick (median 1.0c between opposite-side trades within 5 s, 7,926 pairs). The
  last-trade markout already includes that half-spread, so in quiet play makers earned about 0.5c of
  spread and gave about all of it back to informed flow: **-0.017c per share** (share-weighted).
- Maker rebate, 15% of the 0.05·p(1-p) taker fee at the traded prices: **+0.061c per share** (estimate;
  prices sit far from 0.5 in play, so p(1-p) is small). The whole in-play rebate pool for these 80 games
  is about $2,570/day, shared by every maker.
- Goal losses: 5.8% x 2.36c = 0.137c per quiet share if never cancelled; 0.027c at an 80% cancel rate.

| Case | Edge per share | Maker fills/day for $50 | Share of all quiet in-play volume |
|---|---|---|---|
| Perfect cancel, share-weighted | +0.044c | 114k | 3.0% |
| 80% cancel, share-weighted | +0.017c | 290k | 7.8% |
| No cancel, share-weighted | -0.093c | never | - |
| Perfect cancel, trade-weighted (+0.15c) | +0.21c | 24k | 0.6% |

The last row is the only one that looks easy, and it is not reachable: it weights the many small,
uninformed trades, but a quote at the back of the queue is filled mostly by large trades that sweep
the level, which are the informed ones. EPL liquidity rewards ($100/day per leg) only count while our
quote rests; the in-play two hours are about 1/12 of a day, so 3 legs x $100 / 12 is about $25 per
match, about $36/day across roughly 10 EPL matches a week, and only if we took the whole pool (estimate).

**Verdict: negative.** Reaching $50/day needs 3-8% of all in-play maker volume on the busiest leagues
with near-perfect cancels, for under 0.05c per share. The proposed server job is withdrawn and this line
is closed. (Resting for rewards before kickoff is a different strategy and is not covered here.)
