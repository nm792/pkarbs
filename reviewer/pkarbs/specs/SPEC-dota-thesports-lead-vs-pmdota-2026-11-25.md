# SPEC (pre-registered, locked 25 Nov 2026 10:20Z): TheSports Dota 2 events vs Polymarket Dota own-token books (ledger L22, A14, Reg P15)

Cites **feeds/STANDARD-feed-latency-test.md v1** (Nick's canonical standard) and does not restate its numbers; any deviation is listed below and needs Nick. Known facts: SETTLED A1 (each token its own book), B1 (resolution finer than the lead tested, planted case). MC types per G64. Runs on Prime only (R-039), read-only, from a pinned SHA. Lower priority than the trial-feed timing (PandaScore, Goalserve; Nick 01:29Z): it runs only in idle P-lane slots.

## Data (no new feed; both already recorded on Prime, same host clock)
- Prices: pmdota recorder P122b (`/mnt/HC_Volume_107257520/pkarbs/pmdota/`, pm_dota_books.js at e309b08f75, live since 23 Nov 17:24Z): own-token books for each Dota market (game winner, BO3). Each token priced from its own book; mid = (own best bid + own best ask)/2 of the token named by settlement.
- Feed: TheSports D1 Dota box files (39/40 games captured; manifest = P124b). Receive time = our capture host's ns stamp, never the vendor timestamp.
- Join: team names + start time (STANDARD s.2). Unmatched games listed, not dropped silently.

## Events (fixed before data)
Diffed from consecutive TheSports messages: (1) tower destroyed, (2) Roshan killed, (3) barracks destroyed, (4) team-fight swing = net kill change >= 3 within 20 s. Kills one by one are not events (too frequent for a +-60 s window).
Direction: the event favours the team that made it; the token is that team's game-winner token.

## Measure
Exactly STANDARD s.2: onset = first own-token mid move >= 2c in the event direction inside [-60 s, +60 s] of receive time; lead = onset - receive. Placebo: 10 random event-free times per match (MC type 1, random times on the same data). Resolution: state the TheSports poll interval/2 and the pmdota book cadence; if either is coarser than 1 s, the result is labelled with that resolution and cannot claim a sub-resolution lead.

## Planted case (MC type 2, randomised data, power)
Insert synthetic 3c own-token mid steps 5 s after a random 50% of real event receive times (and remove nothing else); the scorer must report a median lead within +-1 s of +5 s on the planted events and leave the unplanted ones unchanged. A run whose planted case fails is void.

## Bar and verdict
STANDARD s.3 per title (Dota only), stratified by event type (report each; the verdict is on all events pooled across types only if every type has n >= 30, else per type). n < 30 = "unknown, settled when P122b + TheSports have >= 30 events of that type", with the date estimate from the current capture rate. STANDARD s.4 audit by a thread that did not run it before any verdict is relayed.

## Deviations from STANDARD v1
None.

## Delivery
Scorer: adapt feeds/ps_kills_vs_pmcs2.py (same lead/placebo/plant code, already tested) to the TheSports Dota box format and pmdota books; new test file with the planted case above. Code + tests 26 Nov 12:00Z (after P124b says where the box files are and their format). IT run after that.
