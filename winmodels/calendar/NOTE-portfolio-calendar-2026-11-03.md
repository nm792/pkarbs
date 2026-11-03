# Sports portfolio: estimated $/day by month (3 Nov 2026)

**Bottom line.** These figures assume every sport earns what LoL earns per dollar of Polymarket volume. The volumes are what Polymarket actually traded in the same month over the last 12 months. On that basis the portfolio falls short of $500/day in **Nov, Dec and Mar** ($340-414/day). It clears $500 from Apr to Oct, peaking at about $1,900. Without NFL and tennis, where rn1 already trades, it also falls short in Jan (barely) and Mar. Polymarket volume grew strongly over the year (CS2 Oct 2026 was 9x Nov 2025), so next year's weak months will probably be higher than last year's. But only LoL has a per-game profit, and it is simulated. NBA, the one other sport tested, did **not** carry the edge through to the result. So read this as "what each sport would add if the LoL rule works there".

## Update 05:55Z: range from the LoL rerun with corrected fills
The LoL thread reran with fills within 1% of the bid and a 2 s delay. In-sample: 473 games, $150k filled, +$22.7k to result, about **$48/game**. Holdout: +$13.3k over 174 games, about **$76/game**. These replace the $60/game assumption as a low/high range. Yield per $ of volume is still scaled by an assumed $1.67M of Polymarket volume per LoL game, which is the Worlds level. Ordinary-league games trade less, so the true yield per $ is probably higher, and so are these figures.

| Month | All sports, low ($48/game) | High ($76/game) | Without NFL and tennis, low | High |
|---|---|---|---|---|
| 2025-11 | 328 | 519 | 272 | 431 |
| 2025-12 | 275 | 435 | 272 | 430 |
| 2026-01 | 450 | 713 | 402 | 636 |
| 2026-02 | 756 | 1,197 | 549 | 869 |
| 2026-03 | 331 | 524 | 267 | 422 |
| 2026-04 | 1,187 | 1,879 | 864 | 1,369 |
| 2026-05 | 1,114 | 1,764 | 750 | 1,187 |
| 2026-06 | 960 | 1,520 | 554 | 877 |
| 2026-07 | 954 | 1,510 | 688 | 1,089 |
| 2026-08 | 1,504 | 2,382 | 1,030 | 1,630 |
| 2026-09 | 1,400 | 2,216 | 652 | 1,032 |
| 2026-10 | 1,549 | 2,453 | 859 | 1,360 |

Average over the 12 months: all sports $901-1,426/day; without NFL and tennis $596-944/day. Months below $500 on the low case: Nov, Dec, Jan, Mar (and Nov, Dec, Mar on the high case too, apart from Nov all-sports at $519 and Mar at $524). The table below uses $60/game per sport.

## $/day by month, last 12 months of measured Polymarket volume x LoL yield
| Sport | 2025-11 | 2025-12 | 2026-01 | 2026-02 | 2026-03 | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 | 2026-09 | 2026-10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LoL | 95 | 43 | 139 | 269 | 86 | 386 | 380 | 190 | 494 | 596 | 360 | 379 |
| CS2 | 44 | 74 | 76 | 189 | 82 | 229 | 222 | 347 | 207 | 317 | 282 | 398 |
| Dota 2 | 26 | 37 | 19 | 72 | 35 | 151 | 164 | 101 | 140 | 370 | 160 | 215 |
| NFL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | 342 | 356 |
| NHL | 176 | 184 | 264 | 103 | 109 | 230 | 71 | 20 | 0 | 0 | 5 | 67 |
| Tennis (ATP+WTA) | 69 | 4 | 61 | 259 | 80 | 403 | 456 | 508 | 333 | 569 | 593 | 507 |
| Cricket (intl) | 0 | 1 | 4 | 50 | 20 | 4 | 5 | 18 | 19 | 3 | 8 | 15 |
| Cricket (IPL) | 0 | 0 | 0 | 0 | 0 | 80 | 95 | 14 | 0 | 0 | 0 | 0 |
| Rugby | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Total** | **410** | **343** | **563** | **945** | **414** | **1,484** | **1,393** | **1,200** | **1,192** | **1,880** | **1,750** | **1,937** |
| Without NFL and tennis | 341 | 339 | 502 | 686 | 334 | 1,081 | 937 | 692 | 859 | 1,287 | 814 | 1,074 |

NFL shows 0 before Aug 2026 because Polymarket's current NFL series has no events before that date (a data gap, not a real zero). The 2025 season ran Sep-Feb at roughly $340-360/day on this yield. The data and script are in calendar/monthly_volume_2025-11_2026-10.json and pull_monthly.py.

## How the numbers are built
- **$/day = yield x Polymarket volume per day x season factor.**
- **Yield (estimate):** about $60 profit per LoL game (LoL thread, the level Nick accepts) x about 3 games per series, divided by $5.0M of volume per LoL series = **0.0036% of volume**. This is simulated, in-sample, and from before the fill-rule fix. The LoL thread is rerunning it with corrected fills.
- **Volume per day (measured):** Polymarket events by league, 22 Oct-2 Nov 2026, in `winmodels/rank/`. It includes pre-game volume; NBA in-play is about 45% of the total.
- **Season factor (estimate, earlier version only):** volume in each month compared with late October, taken from usual season calendars, not measured: LoL Worlds ends mid-Nov, off-season in Dec, MSI in Jul, Worlds in Oct; NFL Sep-early Feb; NHL Oct-Jun; tennis off-season in Dec; IPL Mar-May; Six Nations Feb-Mar; Rugby World Cup Oct 2027.

## Earlier version: season guesses applied to late-Oct 2026 volume (kept for comparison)
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

On late-Oct volume, no month is below $500 and December is the weakest. The measured table above is the better basis.

## What this does not show
- **Whether the edge exists outside LoL.** In NBA, the event-only rule tested on held-out games made +1-4% at 1 minute with a 0-3 s feed, but lost to the result and filled only about $200 per game. CS2 and Dota 2 cannot be tested yet, because our logged score feed is too slow and sparse (a raw websocket capture to check this is running, 3 Nov 05:46-06:46Z).
- **Rugby and cricket are tiny on Polymarket.** Rugby is about $2.9M/yr. International cricket was about $0.5M/day; the IPL is the one large window. Rugby's value is only in big tournaments, and even the Rugby World Cup multiplier leaves it near $0 at this yield.
- **rn1 already competes in tennis (3.6-6.7% share) and NFL (1.9%).** NFL was dropped on 2 Nov after score-timing tests showed no effect.
- **Capacity:** the yield assumes our fills grow with volume, without moving the price or the queue.

Confidence 5/10: the volumes are now measured, but the profit rate is not. To reach 9 we need: (1) the LoL rerun with corrected fills, giving a real per-game profit; (2) held-out results for CS2 and Dota 2 on a fast feed.

## Addendum 3 Nov 06:05Z: AFL and rugby tournaments (measured volume, gamma API)
**AFL.** Polymarket listed AFL only from 8 Aug 2026 (series 12563; AFLW 12564), so it covered the end of the season and finals only. AFL men: 36 games, $126k total; one game took $96k (North Melbourne v Geelong, 8 Aug), the rest $0.4-9k each. AFLW: 101 games, $8k total. No Grand Final or premiership market found. At the LoL yield (0.0036% of volume) that is about $0.10 per game, so AFL does not fill March unless volume grows 100x+. rn1's share was not checked (the activity API timed out); it does not change the answer at this size.

**Rugby by competition, Jan-Oct 2026** (sum of event volume, by listing month): Six Nations $1.15M (9 matches with volume, about $128k per match; 6 later-round events show $0), Super Rugby Pacific $0.49M, Top 14 $0.45M, Champions Cup $0.28M, Premiership $0.19M, URC $0.17M, NZ v SA series $0.07M. The Rugby Championship series has no events. Total about $2.8M.

**Tournament line (estimate, scaled from Six Nations 2026):**
| Event | Dates | Volume estimate | Our profit at LoL yield |
|---|---|---|---|
| Six Nations 2027 | Feb-Mar 2027, 15 matches | $1.2-2.5M (2026 level up to 2x growth) | $40-90 total |
| Rugby World Cup 2027 | 1 Oct-13 Nov 2027, 48 matches | $6-18M ($128k per match, up to 3x for a global event) | $200-650 total, about $5-15/day |

Only RWC 2023 had one market on Polymarket ($7.8k), so there is no direct comparable. The profit column uses LoL's yield. In markets with no rn1 we could take a larger share of fills; even at 1% of volume and 1% net (rn1's maker margin), RWC 2027 would give 1% x 1% x $6-18M = $600-1,800 total. Rugby stays a capability build (models, feeds, timing) for these events, not a profit line.
