# Stale-ask pickoff across event markets: ranked FLOOR table (26 Nov 2026, offline, R-047)

**Goal:** reliably $200/day automated Polymarket edges, stacked. **Where we stand:** no MEASURED figure. The only own-book evidence is one release (25 Nov Core PCE, SIM +$29.60, P158/P159); this document adds a PRINTS-ONLY floor across 28 family/tier rows. **Item that matters most:** the calendar-anchored rows (CPI+eggs, jobs, GDP, Fed) are the only ones whose "knowable moment" is independent of price; everything marked ONSET needs a trigger source before it can be called a floor at all.

## Method (code in this folder; repo SHA of base = d47a2e3237)
- Universe: Gamma `/events?tag_slug=` for ~50 tags (economy, fed, cpi, jobs, gdp, earnings, box-office, netflix, spotify, app-store, youtube, elon-tweets, politics, trump, elections, awards, oscars, grammys, eurovision, tech, ai, openai, business, ipos, earnings-calls, courts...) -> 18,268 events; sports, weather, crypto excluded by regex. Classified by title into 21 families (`families.py`). Latest 40 closed events per family (80 for macro), up to 20 markets each: **1,034 events, 8,073 markets resolved, 0 fetch errors** (`scan_out.json`).
- Prints: Data API v2 `/v2/trades?condition=`, condition_id asserted per row, whole-second timestamps. Winner token = settlement outcome (oracle proxy for the printed number; measurement only). YES and NO tokens separate.
- Rule: BUY prints on the winner's OWN token, price < 0.95, ts in [R+L, R+60 s]; $200/trade, $2,000/day (UTC) cap on paid notional; edge = sum n*(1-p)/p. No fee deducted (fee schedule UNVERIFIED), so slightly high.
- R: **calendar rows** = the scheduled clock (NY 08:30/10:00, London 07:00, Berlin 11:00; Fed NY 14:00; central banks' own clocks) snapped to the price-jump day, jump = first print after which all winner prints stay >= 0.6 after a print <= 0.5; snap window = clock within 600 s before the jump (median lag R to jump: CPI 16 s, jobs 20 s, GDP 13 s, eggs 34 s, Fed 82 s). **ONSET rows** have no known clock: R = the jump itself, so they are hindsight-defined, include gradual repricing (not only stale quotes) and are **NOT a floor**; L=0 is an artefact there, use L>=2.
- Monthly scaling: mean per tier-event x events/month (listed events ending in last 180 d) x share of scanned events in tier. Samples are the 40 most recent events, so scaling is rough; elections is 25 of ~350/month.
- **Planted checks** (`test_scan.py`, all pass; each can fail): synthetic stale winner print at R+5 must be found with exact size/price; pre-release print at R-1 s, price 0.96, SELL side, loser token and R+61 s print must all be rejected; L=15 must miss the R+5 print; a mutated window starting before R is shown to leak the pre-release print; jump detector finds a planted jump and rejects a planted no-jump; clock snap accepts 13:30:20Z and rejects +700 s and non-calendar families; caps enforced ($200/trade, $2,000/day).
- Resolution: prints are whole seconds, so **100/250/500 ms and 1 s cannot be separated here** (L=0 vs 2 vs 5 vs 15 only; calendar rows barely change between L=0 and L=5, i.e. stale quotes lasted seconds). Sub-second needs the ms book recorder. P158 already showed SIM identical at 0.5 s and 2 s for PCE; that oddity is being checked elsewhere and is not cited as a result.

## Ranked table (floor edge $/day, L = seconds after R; rank by L=5)
| rank | family | R source | events/mo (listed, 180d) | scanned | tier events | with >=1 print at L=5 | prints L=5 | $ paid/event (cap $200/trade) | floor edge $/day L=0 | L=2 | **L=5** | L=15 | top event share | stack layer |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| 1 | elections_results | ONSET (price jump; hindsight, NOT a floor) | 348.5 | 40 | 25 | 8 | 44 | 100 | 692.1 | 388.9 | **296.4** | 128.2 | 70% | UNPROVEN (needs trigger source) |
| 2 | launches_company | ONSET (price jump; hindsight, NOT a floor) | 39.0 | 40 | 33 | 12 | 230 | 187 | 181.2 | 100.7 | **72.0** | 43.0 | 26% | UNPROVEN (needs trigger source) |
| 3 | elon_tweets | ONSET (price jump; hindsight, NOT a floor) | 46.5 | 40 | 32 | 11 | 113 | 118 | 118.9 | 59.9 | **57.1** | 39.9 | 25% | UNPROVEN (needs trigger source) |
| 4 | announcements_appointments | ONSET (price jump; hindsight, NOT a floor) | 17.2 | 40 | 32 | 15 | 477 | 305 | 92.0 | 58.2 | **53.3** | 41.0 | 30% | UNPROVEN (needs trigger source) |
| 5 | cpi_inflation | calendar clock (snap to scheduled time) | 5.5 | 69 | 42 | 39 | 295 | 680 | 29.0 | 29.0 | **28.4** | 13.6 | 21% | YES |
| 6 | box_office_opening | ONSET (price jump; hindsight, NOT a floor) | 24.8 | 40 | 35 | 18 | 59 | 94 | 69.6 | 21.0 | **18.7** | 6.0 | 38% | UNPROVEN (needs trigger source) |
| 7 | eggs_prices | calendar clock (snap to scheduled time) | 7.8 | 67 | 13 | 12 | 108 | 654 | 14.5 | 14.5 | **14.5** | 14.2 | 30% | YES |
| 8 | jobs_unemp | calendar clock (snap to scheduled time) | 2.0 | 76 | 48 | 41 | 232 | 489 | 9.2 | 9.2 | **9.1** | 6.7 | 20% | YES |
| 9 | netflix_top | ONSET (price jump; hindsight, NOT a floor) | 38.7 | 40 | 26 | 6 | 41 | 27 | 23.1 | 7.8 | **5.0** | 4.2 | 75% | UNPROVEN (needs trigger source) |
| 10 | mentions_will_say | ONSET (price jump; hindsight, NOT a floor) | 51.2 | 40 | 38 | 5 | 10 | 12 | 19.8 | 4.4 | **4.4** | 3.6 | 67% | UNPROVEN (needs trigger source) |
| 11 | awards_shows | ONSET (price jump; hindsight, NOT a floor) | 13.5 | 40 | 35 | 13 | 35 | 55 | 14.5 | 5.0 | **3.2** | 2.8 | 38% | UNPROVEN (needs trigger source) |
| 12 | youtube_views | ONSET (price jump; hindsight, NOT a floor) | 30.5 | 40 | 31 | 8 | 24 | 15 | 35.2 | 4.8 | **3.2** | 3.0 | 41% | UNPROVEN (needs trigger source) |
| 13 | gdp | calendar clock (snap to scheduled time) | 3.3 | 50 | 10 | 6 | 67 | 633 | 3.0 | 3.0 | **2.8** | 2.4 | 35% | YES |
| 14 | fed_decision | calendar clock (snap to scheduled time) | 1.8 | 57 | 9 | 8 | 95 | 609 | 2.5 | 2.5 | **2.5** | 2.1 | 43% | YES |
| 15 | hormuz_ships | ONSET (price jump; hindsight, NOT a floor) | 11.5 | 40 | 36 | 6 | 9 | 12 | 20.7 | 1.3 | **1.3** | 1.2 | 62% | UNPROVEN (needs trigger source) |
| 16 | eggs_prices | ONSET (price jump; hindsight, NOT a floor) | 7.8 | 67 | 26 | 5 | 10 | 16 | 3.2 | 1.0 | **0.4** | 0.2 | 34% | UNPROVEN (needs trigger source) |
| 17 | earnings_beat | ONSET (price jump; hindsight, NOT a floor) | 109.5 | 40 | 27 | 2 | 3 | 2 | 61.3 | 0.6 | **0.4** | 0.3 | 74% | UNPROVEN (needs trigger source) |
| 18 | cpi_inflation | ONSET (price jump; hindsight, NOT a floor) | 5.5 | 69 | 21 | 4 | 9 | 24 | 1.3 | 0.5 | **0.4** | 0.4 | 77% | UNPROVEN (needs trigger source) |
| 19 | gdp | ONSET (price jump; hindsight, NOT a floor) | 3.3 | 50 | 32 | 4 | 14 | 39 | 3.3 | 0.4 | **0.4** | 0.2 | 41% | UNPROVEN (needs trigger source) |
| 20 | court_legal | ONSET (price jump; hindsight, NOT a floor) | 1.5 | 40 | 20 | 4 | 7 | 41 | 1.5 | 0.7 | **0.3** | 0.1 | 46% | no |
| 21 | spotify_chart | ONSET (price jump; hindsight, NOT a floor) | 13.3 | 40 | 29 | 4 | 8 | 2 | 9.9 | 1.6 | **0.3** | 0.2 | 57% | no |
| 22 | ecb_boj_boe_bor | ONSET (price jump; hindsight, NOT a floor) | 3.3 | 52 | 7 | 2 | 7 | 29 | 0.7 | 0.3 | **0.3** | 0.3 | 57% | no |
| 23 | treasury_yield_gold | ONSET (price jump; hindsight, NOT a floor) | 2.3 | 40 | 27 | 4 | 9 | 12 | 0.7 | 0.2 | **0.2** | 0.2 | 40% | no |
| 24 | app_store_rank | ONSET (price jump; hindsight, NOT a floor) | 15.7 | 40 | 34 | 3 | 6 | 1 | 2.8 | 0.3 | **0.2** | 0.1 | 38% | no |
| 25 | resolution_by_tweet | ONSET (price jump; hindsight, NOT a floor) | 0.2 | 23 | 15 | 3 | 31 | 167 | 0.2 | 0.1 | **0.1** | 0.1 | 69% | no |
| 26 | jobs_unemp | ONSET (price jump; hindsight, NOT a floor) | 2.0 | 76 | 22 | 3 | 16 | 12 | 0.4 | 0.1 | **0.0** | 0.0 | 61% | no |
| 27 | tsa_passengers | ONSET (price jump; hindsight, NOT a floor) | 0.2 | 40 | 29 | 2 | 2 | 1 | 0.1 | 0.0 | **0.0** | 0.0 | 93% | no |
| 28 | fed_decision | ONSET (price jump; hindsight, NOT a floor) | 1.8 | 57 | 9 | 0 | 0 | 0 | 0.2 | 0.0 | **0.0** | 0.0 | 0% | no |

How to read: calendar rows are floors from prints (a print is a fill someone else took, so we would share it). ONSET rows are indicative only. "Stack layer" = floor >= $1/day at L=5, >= 5 events with a print, top event < 50% of total; ONSET rows cannot exceed UNPROVEN. 291 of 1,034 scanned events had no jump at all (winner already priced), so those add 0.

## Verdicts (stand-alone floor / stack layer / what settles it)
- **CPI + eggs (BLS, same 08:30 ET release):** $28.4 + $14.5/day floor at L=5, 5.5 + 7.8 events/month, 20-30% top-event share. Stack layer YES (floor). Settle: own-book depth at <=0.90 at the next CPI, Thu 10 Dec 13:30Z (already in the PCE recorder plan).
- **Jobs/unemployment:** $9.1/day, 2 releases/month, 41 of 48 events had prints. Stack layer YES. Settle: Fri 4 Dec 13:30Z capture.
- **GDP ($2.8) and Fed decision ($2.5):** small, 43% top-event on Fed. Stack layer YES but tiny. Settle: Dec FOMC 9 Dec 19:00Z capture.
- **Elon Musk tweet counts, launches/company, announcements/appointments, elections, box office, Netflix, mentions, awards, YouTube:** ONSET only. Headline $ (e.g. elections 296, launches 72, tweets 57, announcements 53) are NOT floors: the clock is hindsight, many events are long-dated "by..." ladders that repriced gradually, and elections is 70% one French-election event. Stack layer: UNPROVEN. Settle: for each, a named trigger feed with its own timestamp (tweet count final = period end; box office = studio/Comscore Sunday estimate; Netflix = Tuesday Top 10 page; mentions = live transcript word time; awards = envelope reading; appointments = White House/press release) plus the own-token book recorder for 10 releases; until then no $/day claim.
- **Earnings beat, TSA, app store, Spotify, court, resolution-by-tweet, treasury/gold, central banks:** below $0.5/day or unanchored. Earnings stale-ask is negligible after the report; its edge (I-18) is pre-report mispricing, a different mechanism.

## Recorder plans (top 3 actionable)
1. **CPI + eggs + core (BLS), Thu 10 Dec 13:30Z (verify BLS schedule):** reuse `it/pm_event_books.js` on every CPI, Core CPI, inflation MoM/YoY and eggs event; window T-30 to T+30 min, both tokens, ms stamps, top 3 levels, `seconds_delay` per market; router starts T-90 min, health read T-60 (IT-OPS 1335Z). Print source: BLS release page poll + fastest wire, time it against first jump. Decision-to-fill with a preloaded order below.
2. **Jobs + unemployment, Fri 4 Dec 13:30Z:** same recorder; 12-14 brackets; same scorer for L = 0.1, 0.25, 0.5, 1, 2, 5 s on ms books.
3. **Elon tweet count (weekly bracket, period end per market rules):** the period end is a fixed clock, so it is a calendar-type row if the rule text confirms the exact second; otherwise needs the xtracker count feed. Recorder: all brackets of the current weekly event, T-10 min to T+5 min at period end. Verify the end time before scheduling.
(Dec FOMC 9 Dec 19:00Z stays on the existing plan.)

## Preloaded orders (Nick 04:19Z), from Polymarket docs
- Order structure carries tokenId, price, size, expiration and a millisecond timestamp for uniqueness, signed offchain by the account signer ([Place Orders](https://docs.polymarket.com/trading/place-orders.md), [Order Lifecycle](https://docs.polymarket.com/concepts/order-lifecycle.md)). So one order per bracket and per token can be signed before the print; at the print send only the winner's. Price must be set in advance, so use a marketable limit at 0.95 (price improvement means the fill is at the actual ask) with FOK/FAK; do not rely on GTD (must expire >= 3 min ahead and expires 1 min early).
- Delay: marketable orders can be held by a taker delay (250 ms on selected crypto/finance up-down markets) or a sports/game seconds-delay; held orders cannot be cancelled and are re-validated at expiry. The PCE markets read `seconds_delay` 0 on 24 Nov (SPEC). Re-read per market before each release; REFUSE if unknown.
- Rate limits: per-signer order bucket, `POST /order` 1 token, `POST /orders` one token per order; Standard tier 40/s with burst 60, higher tiers by 30-day volume; limiter in warning mode from 24 July 2026, live enforcement date to be announced ([Trading rate limits](https://docs.polymarket.com/api-reference/trading-rate-limits.md)). A release needs about 12-14 tokens, well inside burst. The 15-orders-per-batch cap came from a secondary search result and is UNVERIFIED.
- Not checked: Nautilus preload API specifics, signing latency on Prime, fee formula against the docs Fees page.

## Limits and what would raise confidence
Prints are not own-book depth (R-034), so every $ is a FLOOR or indicative; samples are 25-70 events per row; settlement used as winner; fee not deducted; classification by regex (some false positives, e.g. non-scheduled "by..." titles in macro families); no data was scanned for the 4 Dec/9 Dec/10 Dec releases yet. **Confidence 5/10** that the calendar rows are right in order of magnitude (the floor is real prints, planted checks pass), **3/10** on the ONSET rows, because their R is hindsight. To reach 9: own-book recordings of 3+ BLS releases, a named trigger source per ONSET family, and a Prime re-run from a pinned SHA (R-039).
