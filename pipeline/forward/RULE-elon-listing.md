# PRE-REGISTERED RULE: Elon 48h tweet-count brackets, book capture at listing and resting-bid paper test (19 Nov 2026)
Locked before the first capture. Nothing below may be changed after a number is seen; a change needs an Amendment section dated and signed with the reason.

## Universe and clock
Every new event of gamma series `elon-tweets-48h` (closed=false, event id not seen before). T0 = the local wall-clock second of the first gamma poll that shows the event (polls every 2 s from 15:55Z to 17:40Z, every 30 s otherwise); gamma `createdAt` and `startDate` are stored beside it. Listings so far: 17:07:01Z in EST, 16:07:01Z in EDT.

## Capture (no orders are ever placed)
From T0: `POST clob.polymarket.com/books` for all YES and NO tokens of the event (own books, never derived from the other side): every 1 s until T0+30 min, every 5 s until T0+2 h, every 30 s until T0+6 h, every 5 min until the window opens (end - 48 h). Each snapshot stores t_local at request, t_resp, the exchange timestamp per book, the best 20 asks and best 5 bids per token. Best price is the LAST element of each raw list; code sorts explicitly.

## Model (fixed constants, no refitting)
mu = sum over the 48 window hours of the mean xtracker hourly count for that UTC hour of day over the 21 days before T0 (count so far is 0), times (1 - 0.0342); sd = max(0.3428 * mu, sqrt(mu)). p_i = Phi((hi_i + 0.5 - mu)/sd) - Phi((lo_i - 0.5 - mu)/sd) per bracket. The hourly file must end at or after T0 minus 3 days; otherwise the event is logged STALE and excluded from the primary test.

## Orders (paper)
Bankroll B = $1,000 per event. For each YES bracket with p_i >= 0.10: bid price b_i = floor((p_i - 0.05)/0.01) * 0.01, skip if b_i < 0.02. Kelly fraction f_i = (p_i - b_i)/(1 - b_i); stake = min($100, 0.25 * f_i * B); shares = stake / b_i. The bid rests from T0 until the window opens.
Fill rule, judged ONLY from recorded asks: at every snapshot, if the best ask <= b_i, the order fills at the ASK price (never at b_i) for the displayed size at prices <= b_i, up to the unfilled shares. Same-level double counting is blocked: cumulative shares filled at a price level cannot exceed the largest size ever displayed at that level. Passive fills from trade prints are not credited. Fees ignored (stated, small at tail prices).
Settlement: the winning bracket from gamma outcomePrices after resolution; P&L = shares * (1 - price) for the winner, - shares * price otherwise.

## Pass / fail
Primary metric: ROI on filled stake pooled over non-STALE events, bootstrap over events. PASS needs >= 15 events with any fill, pooled ROI > 0 with the 95% interval above 0, and dollars per day (pooled P&L / calendar days observed) reported next to the interval. Fewer than 15 events with fills = UNKNOWN with the count reported. Diagnostics (not pass criteria): time from T0 to first fill, depth at fill, listing-time ask ladder, fill rate by bracket, hit rate of the highest-p bracket versus the market's highest-priced bracket at T0+30 min.

## Plausibility check within 15 minutes of the first capture (`elon_listing.py check`)
Required: all 10 brackets x YES/NO present; best bid < best ask in every book with price in (0,1); median snapshot gap <= 1.5 s in the first 5 minutes and no gap > 10 s; detection latency T0 - createdAt reported; YES best asks summed across brackets >= 1.0 - 0.02 (they should total about 1 or more); p_i sums to 1 +- 0.02 (clipped brackets included). Any failure is reported at once, not smoothed.

## Amendment 1 (19 Nov 2026 17:30Z, before any fill number was computed)
Observed at the first (late) capture, 17:13Z: five to six minutes after listing the books are nearly empty (YES asks 0.94 to 0.98 for almost every bracket, bids 0.01 to 0.08), so a resting bid is rarely crossed by a posted ask: sellers would hit it directly. The primary test is unchanged (fills only from recorded asks, as ordered). Added, diagnostic only and NOT part of pass/fail: a trade tape (`elon_trades.py`, data-api /v2/trades every 5 s) stored beside the books, so a SELL-side print strictly below a bid price after T0 can later be reported as a possible passive fill. The first event (id 1425784) was captured from T0 = 17:13:00Z, 5 min 59 s after gamma createdAt (17:07:01Z) because the first recorder process died; it is flagged LATE and excluded from the primary test.
