# RN1 re-check and NBA post-only bid evidence (Reviewer, 24 Nov 02:58Z)

Nick 24 Nov 02:51Z: "why would we not be checking 4 in more detail?" Desk work on public data. Paper only.

## A. RN1's real fills, 23 Nov 19:40Z to 24 Nov 02:52Z (Polymarket data-api v2)
Wallet 0x2005d16a84ceefa912d4e380cd32e7ff827875ea (name "RN1"). 4,000 fills from `v2/trades?user=..&taker_only=false`. RN1 was taker on a fill if the same (tx, token, size, price, side) appears in `taker_only=true`; the rest are maker fills. This is a set difference, not an on-chain check.
- Volume $456,157 in about 7 hours. **Maker 84.4% of $** (3,377 fills, $385,054); taker 623 fills, $71,104. **Every fill is a BUY**, so it still runs resting bids only.
- Maker $ by league: NBA $79,983; EPL $78,257; NFL $52,307; Brasileirão $47,898; Serie A $44,552; LaLiga $17,283; WTA $13,409.
- NBA maker $ by market type: totals $38,830, spreads $22,714, moneylines $18,439. RN1 now quotes totals, spreads and first-half totals, not only moneylines.
- Maker fill size: median $17.9, p90 $208, max $3,737. Maker price quartiles 0.22 / 0.47 / 0.60.
- **Resolved P&L (one night, to result, noisy):** maker fills +$9,209 on $263,626 (+3.5%). NBA maker +$4,476 on $42,509 (+10.5%), EPL maker +$4,129 on $78,257 (+5.3%). Taker fills -$3,390 on $18,508 (-18.3%), of which NBA -$2,872 on $17,788. Same split as the 3 Nov decomposition: the maker side earns and the taker side loses.
- **Markouts, NBA maker fills in the 40 largest NBA markets (58% of NBA maker $), 572 fills, $40,261.** These are print-based: "market" = last print on the same token, so they are noisy in thin markets.
  - Moneylines: entry +2.10%, first minute +0.80%, to 10 min +6.81%.
  - Spreads: entry +3.32%, first minute -5.12%, to 10 min +4.66%.
  - Totals: entry -4.74%, to 10 min -3.84%. The last print is stale in thin first-half totals, e.g. paid 0.66 when the last print was 0.52.
  - So print markouts cannot judge totals. The P106e own-token books can.
- Concrete large fills: 00:32:52Z mem-cha 1H total 111.5, 1,034 sh at 0.66, resolved 1. 02:39:43Z cle-chi spread away 1.5, 5,205 sh at 0.28 (unresolved at pull). 02:34:16Z bkn-min spread home 13.5, 262 sh at 0.92, +1 min print 0.88.
- File: nba_rows.json (one row per fill: size, paid, last print, +1 min, +10 min, result).

## B. What the 6 Nov simulation did (notes/project-review-2026-11-06.md @59bec3a46b, rn1/scores/lol/bidsim)
- **Rule:** after a game event, bid at market x 0.975 post-only, hold to result. "Queue-safe" fills on public prints.
- **NBA, 429 games, by feed delay:** 0 s $25.6/game (~$184/day); 2 s $20.2; **5 s $9.6 (~$69/day, range just spans zero)**; 10 s $2.9; 30 s+ negative. The free Polymarket sports stream arrives about 5 s after the play.
- **Warning:** held-out 2026-season games were -$42/game at 0 s on 39 games.
- **Queue:** median 6,300 shares ahead of our bid, MEASURED on only 5 minutes of late-game books. This is the main uncertainty.
- **LoL resting-bid sim (3 Nov):** without event cancels, bids lose 6.2% within a minute in all 6 games. Pulling bids for 30 s after events gives +1.2%, plus about +0.4% rebate. Event-driven sellers are the whole risk.
- **Live:** 0 fills ever (LoL dry run, 62 bids, median queue 1,876 shares ahead).

## C. Facts the Nautilus spec must carry
- NBA game markets read seconds_delay = 0 (2 games, 23 Nov 09:00Z). Post-only orders are not affected by the matching delay either way.
- Fees and rebates come from each market's own feeSchedule (sports_fees_v2: rate 0.03, rebateRate 0.25 on current CS2 match markets; NBA to be read per market).
- Own-token books from P106e (running since 23 Nov 08:58Z, 20/20 tokens). Queue ahead = depth at our price at placement; fill only on trade-through at or past our price.
- Score by markout at 1 min and 10 min plus settlement (MODELLING-PRINCIPLES 12). Sequential stops (13). Capacity from measured depth (14). Event cancel window as a parameter (0, 3, 10, 30 s).

## D. Data-source breakage found while doing this (affects every PK scorer)
- **Polymarket Data API v1 is retired:** `data-api.polymarket.com/trades|activity` return HTTP 410 "Data API v1 has been retired". v2 lives at `/v2/trades` with cursor paging (`pagination.next_cursor`).
- **v2 silently ignores unknown query params:** `markets=` and `condition_ids=` returned other markets' trades; only `condition_id` (or `condition`, `conditionId`) filters. A wrong param name returns plausible but WRONG data.
- **Gamma `/events?...&limit=100` now returns 406;** limit 50 works.

Confidence 6/10. One night of RN1 fills, print-based markouts, and a maker/taker split that rests on the taker_only flag. To reach 9: P106e book-based markouts on RN1's NBA fills (same night), and an on-chain maker check on a sample.
