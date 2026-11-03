# Sports portfolio: estimated $/day by month, Nov 2026 - Oct 2027 (3 Nov 2026)

**Bottom line.** These figures assume every sport earns what LoL earns per dollar of Polymarket volume. On that assumption the portfolio clears $500/day in every month, even without NFL and tennis (December is lowest, ~$525). But only LoL has a per-game profit at all, and it is simulated. NBA, the one other sport tested, did **not** carry LoL's edge through to the result. So read this table as "what each sport would add if the LoL rule works there", not as an expected profit.

## How the numbers are built
- **$/day = yield x Polymarket volume per day x season factor.**
- **Yield (estimate):** about $60 profit per LoL game (LoL thread, the level Nick accepts) x about 3 games per series, divided by $5.0M of volume per LoL series = **0.0036% of volume**. This is simulated, in-sample, and from before the fill-rule fix. The LoL thread is rerunning it with corrected fills.
- **Volume per day (measured):** Polymarket events by league, 22 Oct-2 Nov 2026, in `winmodels/rank/`. It includes pre-game volume; NBA in-play is about 45% of the total.
- **Season factor (estimate):** volume in each month compared with late October, taken from usual season calendars, not measured: LoL Worlds ends mid-Nov, off-season in Dec, MSI in Jul, Worlds in Oct; NFL Sep-early Feb; NHL Oct-Jun; tennis off-season in Dec; IPL Mar-May; Six Nations Feb-Mar; Rugby World Cup Oct 2027.

## $/day by month (estimate)
| Sport | Nov | Dec | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LoL | 309 | 31 | 186 | 248 | 248 | 248 | 186 | 248 | 371 | 248 | 248 | 619 |
| CS2 | 428 | 257 | 214 | 385 | 428 | 428 | 428 | 470 | 385 | 385 | 428 | 428 |
| Dota 2 | 286 | 143 | 200 | 257 | 286 | 257 | 286 | 286 | 257 | 286 | 314 | 228 |
| NFL | 407 | 407 | 326 | 81 | 0 | 0 | 0 | 0 | 0 | 0 | 367 | 407 |
| NHL | 74 | 66 | 74 | 66 | 74 | 89 | 96 | 44 | 0 | 0 | 0 | 66 |
| Tennis | 310 | 52 | 620 | 465 | 517 | 465 | 568 | 620 | 568 | 517 | 517 | 517 |
| Cricket (intl) | 19 | 28 | 28 | 22 | 37 | 111 | 93 | 19 | 19 | 28 | 22 | 19 |
| Rugby | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| **Total** | **1,833** | **984** | **1,648** | **1,525** | **1,591** | **1,598** | **1,657** | **1,687** | **1,600** | **1,464** | **1,896** | **2,285** |
| Without NFL and tennis | 1,116 | **525** | 702 | 979 | 1,074 | 1,133 | 1,089 | 1,067 | 1,032 | 947 | 1,012 | 1,361 |

Months below $500: none on these assumptions. December is the weak month: LoL is off, tennis is off, and esports slow down.

## What this does not show
- **Whether the edge exists outside LoL.** In NBA, the event-only rule tested on held-out games made +1-4% at 1 minute with a 0-3 s feed, but lost to the result and filled only about $200 per game. CS2 and Dota 2 cannot be tested yet, because our logged score feed is too slow and sparse (a raw websocket capture to check this is running, 3 Nov 05:46-06:46Z).
- **Rugby and cricket are tiny on Polymarket.** Rugby is about $2.9M/yr. International cricket was about $0.5M/day; the IPL is the one large window. Rugby's value is only in big tournaments, and even the Rugby World Cup multiplier leaves it near $0 at this yield.
- **rn1 already competes in tennis (3.6-6.7% share) and NFL (1.9%).** NFL was dropped on 2 Nov after score-timing tests showed no effect.
- **Capacity:** the yield assumes our fills grow with volume, without moving the price or the queue.

Confidence 4/10. To reach 9 we need: (1) the LoL rerun with corrected fills, giving a real per-game profit; (2) held-out results for CS2 and Dota 2 on a fast feed; (3) volume measured month by month from Polymarket's history instead of season guesses (this is pullable from gamma by series and month).
