# Do Pinnacle / bet365 / 1xbet move before the Polymarket price? (5 Nov 2026)

**Answer: no. Pinnacle moves about 2 s before Polymarket's trade prints in tennis, bet365 about 1 s before, and 1xbet about 4 s after. Only 4-6% of tennis matches show a book leading by 5 s or more. The event rule needs the event 5-10 s before the price, so book prices are not a usable faster feed.** Confidence 7/10.

## Data (raw, all measured)
- Book prices: OddsPapi `/v4/historical-odds` (free), pulled on the server by Hermes for 4 Nov 00:00Z to 5 Nov 12:00Z. That gives 198 fixtures: tennis, 25 CS2, 1 LoL and 5 Dota. Raw: `rn1/scores/oddspapi/2026-11-04b/oddspapi_2026-11-04b.tar.gz`. Timestamps are OddsPapi ingest time; OddsPapi says that is about 1 s after Pinnacle and 4-10 s after bet365.
- In-play history is dense for Pinnacle (median 175 price changes per tennis match, 168 per CS2 match) and for 1xbet. bet365 is sparse on esports (3-23 per match), so bet365 esports can't be tested.
- Polymarket: v2 trades for the matched markets (`out/pmtrades_2026-11-04.tar.gz`), plus our 1 s order books for CS2 on 4 Nov (`/mnt/project-files/cs2-feeds/2026-11-04`, 08:50-12:21Z only).
- Matched: 51-52 singles tennis matches, 3-4 CS2 (match winner) and 1 LoL (GEN-LYON game 1).

## Method
Cross-correlation of 5 s price changes on a 1 s grid, lags -60..+60 s, pooled over matches (`xcorr.py`). The peak lag is where book moves line up best with Polymarket moves.

A first, event-based method (`lead.py`: for each PM jump, when did the book first cross half the move) showed books 10-22 s "first". **It failed its placebo:** the same code run at random times 15 min away also showed books "first" 53-60% of the time with a median of -10 to -16 s, because slow drift crosses the threshold early. Its numbers are not used.

## Results (cross-correlation, measured)
| Sport / book | PM side | Matches | Book lead at peak | Corr at peak | Corr if book were 10 s first |
|---|---|---|---|---|---|
| Tennis / Pinnacle | trades | 51 | **+2 s** | 0.34 | 0.06 |
| Tennis / bet365 | trades | 52 | +2 s pooled (+1 s per-match median) | 0.18 | 0.04 |
| Tennis / 1xbet | trades | 52 | -3 s (book later) | 0.17 | 0.04 |
| CS2 / Pinnacle | trades | 3 | +2 s | 0.14 | 0.05 |
| CS2 / 1xbet | **1 s books** | 2 | **-10 s (book later)** | 0.35 | 0.01 |
| LoL / Pinnacle | trades | 1 | +2 s | 0.16 | 0.01 |

Per-match tennis peaks (corr > 0.1): Pinnacle median +2 s, 2 of 50 matches at >= 5 s; bet365 median +1 s, 3 of 47; 1xbet median -4 s, 2 of 50.

## Caveats
- PM trade prints come after the PM quote moves (median gap between trades before a jump is 14 s), so a book "lead" over trades overstates its lead over the PM price. The true lead is 2 s or less.
- CS2 and LoL samples are tiny (1-4 matches). Bet365 esports history is too sparse to test.
- Getting Pinnacle live through OddsPapi needs their B2B WebSocket plan (REST has cooldowns). That isn't worth buying given the result.

## To reach 9/10
Repeat with 1 s PM books for tennis (log books for 20+ matches) and 10+ CS2/LoL matches.

## Addendum (5 Nov 04:25Z): is a 2 s lead enough? Direct test with Pinnacle/bet365 as the trigger
Nick: "why do we need 5-10 seconds and not 2?" Script `winmodels/tennis/hist/pin_trigger.py`, output `out_pin_trigger.json`.
- **Where the 5-10 s came from.** It was partly data and partly my wording. The trade-based tennis delay curve (1,895 matches, NOTE-sports-adv-and-delay-curves section 5) gives $3.97/match 5 s before the price onset, $1.99 at onset, $1.29 at +2 s and ~$0 at +5 s, as an upper bound (oracle side, no queue). So the data says value exists only up to about the onset. "5-10 s before" overstated what is needed; "at or before onset" is right.
- **Lead vs PM price onset (measured, same onset definition):** Pinnacle steps of 1.5pp or more come a median 2.4 s before the PM onset (IQR -0.2 to 7.6 s; first 74% of the time; 2,387 steps on 50 matches). bet365 comes 0.8 s before (IQR -8.4 to 7.4; first 54% of the time).
- **Backtest (book step = trigger and side; bid PM mid x 0.975 from trigger + latency, while PM hasn't caught up; trade-based fills, queue ignored = optimistic; held to result):**
  - Pinnacle, bid lives 10 s: latency 0.5 s gives $1.76/match (90% -$4.0 to +$9.9; 10 of 50 matches filled; ex-top-5 -99%). 1.5 s gives -$1.22. 3 s gives -$0.08. 5 s gives -$4.86.
  - Pinnacle, bid lives 30 s: -$4.9 to -$17/match at every latency.
  - bet365, 10 s: 0.5 s $5.55 (90% -$9.0 to +$23.4), 1.5 s -$0.24, 3 s +$2.41, 5 s -$3.45; ex-top-5 -99% throughout. 30 s: about $0 or negative.
- **Verdict:** a 2 s lead is real but not enough to make money. Fills at market - 2.5% are $2-16/match, and every result range spans zero (the best is ~$1.8/match = ~$110/day at 61 matches/day, all from 5 matches). Live access needs OddsPapi's paid B2B WebSocket, and realistic latency (1.5 s+) is negative. No tennis order books were recorded, so queue position is not modelled; that makes these numbers optimistic. Confidence 6/10.
