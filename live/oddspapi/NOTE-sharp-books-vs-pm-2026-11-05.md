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
