# How rn1 makes its money, 22 Oct - 2 Nov 2026 (fill-by-fill, 3 Nov 2026)

Wallet 0x2005d16a84ceefa912d4e380cd32e7ff827875ea. Every fill in two windows, all buys, all markets resolved:
- Week 1: 22 Oct 02:04Z - 29 Oct 02:03Z, 72,744 fills, $17.95M.
- Week 2: 29 Oct 02:04Z - 2 Nov 06:00Z (4.2 days), 38,670 fills, $10.66M.

## Method (exact identity, no model)
For each fill (shares s, price paid p, result P = 0 or 1, Polymarket 1-minute price series m(t) for that outcome):

    s*(P - p) = s*(m0 - p)        entry: price paid vs the market price at the fill
              + s*(m60 - m0)      first minute after the fill
              + s*(m600 - m60)    1-10 min
              + s*(P - m600)      10 min to the result

The parts always sum to the fill's trade P&L. Maker or taker per fill from the takerOnly flag (week 1 also matched on-chain exactly). Fees: week 1 per fill from on-chain OrderFilled word 4 ($49,592, all on taker fills); week 2 from Polymarket's own P&L series. Rebates and rewards: activity rows paid in each window.

## Answer: net +$314k over 11 days = three parts (MEASURED)

| Part | Week 1 | Week 2 | Both | % of its $ |
|---|---|---|---|---|
| **1. Resting bids filled (maker), trade P&L** | +212.8k | +28.1k | **+240.9k** | 0.96% of $25.0M |
|  of which entry: bought below market | +413.7k | +221.0k | +634.7k | 2.54% |
|  of which first minute: price moves against it | -166.1k | -76.3k | -242.4k | -0.97% |
|  of which after the first minute | -34.8k | -116.6k | -151.4k | -0.61% |
| **2. Taker buys** (trade P&L, then fees) | +127.3k, -49.6k | -114.4k, -20.4k | **+12.9k, -70.0k = -57.1k** | |
| **3. Rebates and rewards** | +81.7k | +48.7k | **+130.4k** | 0.46% of $28.6M |
| **Total** | **+372.2k** | **-58.0k** | **+314.2k** | 1.10% |

Cross-check with Polymarket's own P&L series for rn1 (/v2/user-pnl, raw/pnl_1m_2026-11-03.json): trade P&L 22-29 Oct 00Z +$355k (ours +$340k), 29 Oct-2 Nov 00Z -$92k (ours -$86k); economic P&L over 22 Oct-2 Nov 00Z +$311k.

### Reading
- rn1 is a resting-bid market maker. Its bids fill on average 2.5% below the market price. About 40% of that is lost within a minute (the people who hit its bids often know something), and a further quarter later. It keeps about 1% of its maker volume, plus about 0.5% in rebates and rewards. That is the whole engine; it matches the lifetime figure (2.2% of volume, falling to 1-2% recently).
- Its taker buying roughly breaks even before fees over the 11 days (+$13k on $3.6M) and loses after fees. All its fees come from these buys.
- Week-to-week results swing by $100k+ with game outcomes, so a single week can mislead (week 2 was negative).

### CS2 specifically
- Week 1 CS2 taker buys made +$187k (map winners paid 0.467, won 0.594). **Week 2 the same buys lost $50k (-19%).** So the week-1 CS2 result is not evidence of a lasting forecasting edge; most likely variance.
- CS2 maker fills: week 1 +$54k on $2.54M, week 2 +$5k on $1.05M.
- rn1's CS2 buying: 29 Oct $660k, 30 Oct $363k, 31 Oct $266k, 1 Nov $18k, 2 Nov $0, 3 Nov to 03:15Z $0, while Polymarket listed big CS2 games (FURIA-FaZe $2.40M volume, MOUZ-TYLOO $0.73M). No CS2 fills to match to our live round scores yet.

### By sport, maker trade P&L (week 1 / week 2)
Soccer and other +170k / -58k; tennis +35k / +34k; CS2 +54k / +5k; US sports -42k / +47k. Each sport alone is within noise (event bootstrap, out/boot.json); the entry and first-minute parts are consistent in sign in every sport and both weeks.

## Not settled
- The price series is CLOB prices-history at 1-minute points; not confirmed whether it is the mid or last trade. This moves amounts between "entry" and "first minute" but not the totals of part 1.
- Week 2 fees are from Polymarket's daily P&L series (29 Oct-2 Nov 00Z), not per fill.
- calib.json (time-weighted price vs result) has correlated points within markets; not used for conclusions.
- The earlier a4.py figure for week 1 (+$296k) used the 29 Oct snapshot when 279 markets were still open; with all resolved it is +$340k.

## Files
Repo rn1/decomp/: scripts (decomp.py, cs2detail.py, boot.py, oos.py, pull_activity.py, pull_taker.py, v2_to_v1.py, calib.py); out/ (decomp_full.json = week 1, decomp_2026-10-29_11-02.json = week 2, oos_2026-10-29_11-02.json, cs2detail.json, boot.json); raw/ (activity and taker fills 29 Oct-3 Nov, market metadata, Polymarket P&L series).
Price series: /mnt/project-files/rn1/raw/prices/clob_all_2026-10-22_29.tar.gz (week 1, 15,184 tokens) and clob_2026-10-29_11-02.tar.gz (week 2, 7,564 tokens).

Confidence 8/10. To reach 9: confirm the price series is the mid (compare with live book snapshots), and one more week of fills.
