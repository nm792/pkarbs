# Sports MECE NO side re-score (20 Nov 2026)

**Goal:** find un-publicised edges and stack them toward $500/day. **Where this stands:** the NO side is now scored on own-token asks for the first time, on the only both-token data readable from this container (4-5 Nov captures); result 0 detections. **Item that matters most:** the new recorders (pmcs2, pmdota, NHL P86n) record two-token moneyline markets only, so they can never see a 3-leg (home/draw/away) set, which is where the old MECE runs found gaps.

## What was scored
Script `pair_score.py` (this folder). Per two-token market, each token priced from ITS OWN book (asks for buy, bids for sell); never NO = 1 - YES.
- Buy both tokens at own asks (the "buy every NO" set for a 2-way market): edge = 1 - askA - askB - fee(A) - fee(B).
- Mint a $1 set and sell both at own bids: edge = bidA + bidB - 1 - fees.
- Fee = 0.05 x p x (1-p) per share per leg (memory note, PM sports fee 20 Nov).
- Fill walks the book to depth; delay row fills from the book 1000 ms after detection (secondsDelay 1 on these markets); delay 0 also shown.
- Not modelled: neg-risk conversion (does not apply to a single 2-token market), taker rebate (tier starts 0%).

## Data (checked first)
Inputs: /mnt/project-files/nhl-feeds/2026-11-05/run1-3 and cs2-feeds/2026-11-04{,-lowtier,-queue}, rows = full book snapshots, both tokens present for 8 NHL and 97 CS2 markets (26+55+16).
| Dataset | markets with both tokens | observations | min askA+askB | detections (delay 0 / 1 s) |
|---|---|---|---|---|
| nhl run1 | 2 | 22,596 | 1.001 | 0 / 0 |
| nhl run2 | 4 | 28,508 | 1.001 | 0 / 0 |
| nhl run3 | 2 | 11,936 | 1.001 | 0 / 0 |
| cs2 2026-11-04 | 26 | 155,304 | 1.001 | 0 / 0 |
| cs2 lowtier | 55 | 281,534 | 1.001 | 0 / 0 |
| cs2 queue | 16 | 29,566 | 1.001 | 0 / 0 |
Sell-both side also 0 detections in every row. Stand-alone $/day: $0 measured. Stack layer: no, on this data.

## Why this does not settle the question
1. These are 4-5 Nov captures of 2-way markets, not 20 Nov recorder output (that sits on the server storage box; I cannot read it). NHL P86n has no games until 21 Nov 18:00Z (IT note 03:45Z).
2. The old MECE runs found gaps in 3+ leg neg-risk sets (European football, mostly). pmcs2/pmdota/NHL record `moneyline` with exactly two tokens (`it/pm_sport_books.js` pickMarkets). A 2-token market is a single book pair; askA+askB < 1 would need a crossed book. Zero in about 530k observations is the expected result, so it is weak evidence about 3-leg sets.
3. To settle: record both tokens of every leg of 3-way soccer (home/draw/away) and other neg-risk sports events, a few weeks including in-play, then score "buy every NO" and "buy every YES" on own asks with the 1 s delay and neg-risk conversion cost. Needs a recorder change (IT/Prime Bot deploys, thread writes code) and disk: soccer is more books than NHL.

Confidence 6/10 that the zero is correct for these data; 3/10 that it says anything about 3-leg sets. To reach 9: score the 19-20 Nov pmcs2/pmdota output (IT to run `pair_score.py <dir>` on the storage box) and decide whether to add a 3-leg soccer both-token recorder.
