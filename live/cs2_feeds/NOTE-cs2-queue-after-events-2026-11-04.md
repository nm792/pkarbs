# CS2: is the queue at our bid pulled in the first seconds after an event? (4 Nov 2026)

Thread "Check if CS2 queue clears after events". Answer: **no**. Confidence 7/10.

## Data
- Two 1 s full-depth book captures (`capture.py`, `POST /books` every 1 s) + sports WS + data-api v2 trades:
  - `raw/2026-11-04/` (09:00-10:45Z, from the faster-feed thread)
  - `raw/2026-11-04-queue/` (11:37-12:31Z, this thread; MongolZ-FURIA map 3 + NaVi-Falcons)
  - copies in `/mnt/project-files/cs2-feeds/2026-11-04*/`
- Tier 1 (IEM Beijing): 76 event x rising-token rows (53 MongolZ-FURIA, 23 NaVi-Falcons). Events and the market
  move time Tm as in `analyze.py` (Tm = start of the largest 3 s mid step around the WS round update).
- Scripts: `queue.py` (per-second size at our prices, cancels vs fills), `queue_detail.py` (when the new level becomes
  placeable, no-event control), `queue_pos.py` (our queue position after joining, ladder-move signature).
  Outputs in `raw/2026-11-04-queue/out/`.

## Two prices we could bid at (both maker, mid x 0.975, i.e. 2.5% RELATIVE, floored to the 1c tick)
Tm = start of the largest 3 s rise in the token's mid in [WS update - 75 s, WS update + 5 s]. Mid = (best bid + best
ask)/2 of that token's own book in one 1 s snapshot (YES and NO books mirror exactly: NO bid = 1 - YES ask).

**Fix 12:45Z (PR #84):** the old price was computed from the median mid 45-90 s before the WS update (inherited from
`analyze.py`), not the live mid. In some rows that put it at the ask or far under the market. Now it is the mid 2 s
before Tm x 0.975. Old-price numbers below are rerun; new-price and lower-tier numbers did not use it and are unchanged.
| tier 1, medians over 76 rows | -10 s | -2 s | Tm | +2 s | +3 s | +5 s | +10 s | +30 s |
|---|---|---|---|---|---|---|---|---|
| size at OLD price (mid 2 s before the move x 0.975) | 3,152 | 3,267 | 2,998 | 2,385 | 1,625 | 1,488 | 1,500 | 1,384 |
| size at NEW price (post-move mid x 0.975) | 0 | 0 | 0 | 0 | 2,718 | 3,475 | 3,444 | 3,570 |

1. **Old price** (median 1 tick under the best bid): 51% of the size there 10 s before the move is still there at
   +5 s, 47% at +30 s (no-event control: 96% after 15 s, 91% after 40 s). So events do trigger cancels, but half the
   queue stays. Of 860k shares removed in -10..+30 s, 2.2k (0.3%) were fills; the rest were cancels. 37% of
   cancelled size reappeared at another bid level of the same token in the same second (looks like re-pricing).
2. **New price:** it becomes placeable as a maker (best ask above it) a median 3 s after Tm. At the first 1 s snapshot
   when it is placeable, a median **2,522 shares** already rest there (25th percentile 858). It was under 100
   shares in only 6 of 76 rows. The queue forms in the same second the market moves.
3. **After joining at the new price** (5 shares, first placeable second): ahead of us 2,522 -> 1,930-1,970 at +5 s,
   1,140-1,500 at +10 s, 300-1,090 at +30 s (pro-rata cancels vs back-first cancels). We reach the front within
   30 s in 15-19 of 76 rows. Only 6.5k shares printed at that price across all 76 windows (21 rows had any).
4. **Same makers?** The book does not show owners and the trades list shows only takers. In the second the new level
   fills, 1.02M shares vanish from the token's other bid levels against 230k added at the new price (65 rows). That
   fits bots moving whole ladders up with the mid. It is a signature, not proof.

## What it means
- At our current feed speed (sports WS a median 31 s behind the price on these tier-1 rows), or at any speed level
  with the price, the queue blocks us: the new level is re-stacked in the same 1 s snapshot it becomes reachable.
- A feed AHEAD of the price helps less than it seems. Our rule always bids 2.5% under the LIVE market, so before the
  move a fast bot bids the old price (behind ~3,300 sh). The post-move price (2.5% under where the market is about to
  go) is above the pre-move best ask in 62 of 76 tier-1 rows (median move 5c, spread 1c, so it is above the ask
  whenever the move exceeds ~2.5% + half a cent); a maker-only bid can't rest there until the ask moves (the same moment the bots re-stack;
  who wins that race is sub-second and unmeasured). In the other 14 rows the new price is already a resting level with
  a median 2,044 sh on it before the move.
- Even when churn moves us to the front, very few prints reach the level. Tier-1 CS2 maker fills at mid-2.5% stay
  near zero for a 5-share order behind ~2,500 shares.
- Lower tiers (3 games: ILLYRIANS-Bebop and megoshort-Honvéd (CCT qualifier), BRUTE SQ-ICP (United21); 79 rows; `lowtier.py`, `out/lowtier.json`): median 50 sh at the new
  price when it becomes placeable (under 100 in 52 of 79); only 756 sh printed there in 30 s across all 79 events (9
  rows had any). Sports WS lag vs the price: median 41.5 s. Slow bot at our current feed (join at R, mid(R) x 0.975):
  205 sh ahead, 768 sh printed at or below our price in 30 s (4 rows), fills beyond the queue in 2 of 79 events
  (200 sh at cap 100, 581 at cap 500). Markout +$8.5/+$17.8 at 60 s, +$1/-$29 at 300 s. That's ~$0.1-0.2 per event,
  ~$3-6 per game at 60 s with an unknown sign held longer. Estimate (not measured): under ~$50/day across lower-tier
  CS2, not distinguishable from zero on 2 fills. Lack of sellers, not the queue, is the blocker there.

## Limits
- 1 s polling: we can't see order within a second, or cancel/replace that nets to zero inside a second.
  Millisecond data needs the CLOB market WS (ws-subscriptions-clob.polymarket.com, not allowlisted here; Hermes could run it).
- Two tier-1 matches, one tournament. Trade timestamps are whole seconds (fills matched with +-1 s slack).
