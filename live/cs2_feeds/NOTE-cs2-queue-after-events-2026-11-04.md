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

## Two prices we could bid at (both maker, mid - 2.5%)
| tier 1, medians over 76 rows | -10 s | -2 s | Tm | +2 s | +3 s | +5 s | +10 s | +30 s |
|---|---|---|---|---|---|---|---|---|
| size at OLD price (pre-event mid x 0.975) | 2,548 | 2,394 | 2,102 | 1,975 | 2,066 | 1,692 | 1,756 | 1,561 |
| size at NEW price (post-move mid x 0.975) | 0 | 0 | 0 | 0 | 2,718 | 3,475 | 3,444 | 3,570 |

1. **Old price:** 49% of the size there 10 s before the move is still there at +5 s, 44% at +30 s (no-event control:
   94% after 15 s, 89% after 40 s). So events do trigger cancels, but half the queue stays. Of 737k shares removed
   in -10..+30 s, 6.5k (0.9%) were fills; the rest were cancels. 37% of cancelled size reappeared at another bid
   level of the same token in the same second (looks like re-pricing).
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
- A speed edge of "the first few seconds" doesn't exist at 1 s resolution: the queue at the new price is there in the
  same snapshot the price becomes reachable. Getting in front would need sub-second reaction to the market itself
  (or a kill feed that beats the market), and our best CS2 feed is ~16 s behind the price.
- Even when churn moves us to the front, very few prints reach the level. Tier-1 CS2 maker fills at mid-2.5% stay
  near zero for a 5-share order behind ~2,500 shares.
- Lower tiers (CCT etc.) have ~45 shares at the new price when it becomes placeable, so the queue is not the blocker there.

## Limits
- 1 s polling: we can't see order within a second, or cancel/replace that nets to zero inside a second.
  Millisecond data needs the CLOB market WS (ws-subscriptions-clob.polymarket.com, not allowlisted here; Hermes could run it).
- Two tier-1 matches, one tournament. Trade timestamps are whole seconds (fills matched with +-1 s slack).
