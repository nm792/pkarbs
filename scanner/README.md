# MECE scanner (alert-only)

Watches Polymarket (and Kalshi, read-only) for locked-payout structures and logs every alert with its duration and what it would have paid. **It never places orders.** Base case is Polymarket-only (`--venues pm`). Kalshi pairs are still priced, but they are marked `ALERT-ONLY` until Kalshi verification clears.

## What it prices
A *structure* is a set of buckets that together cover every outcome. Each bucket lists instruments (one or more legs bought together) that pay $1 in that bucket's outcomes. Buying the cheapest instrument per bucket gives a payout of at least $1 in every state. `engine.walk()` takes sets greedily through real book depth, adds each venue's taker fee per fill level (Kalshi 0.07·p·(1−p) rounded up to the cent; Polymarket `feeSchedule.rate`·p·(1−p), which is 0 on political markets), and stops when the marginal set costs more than `1 − min_edge`. It reports sets, cost, fees, profit, % return, and best and worst marginal price.

| Type | Venues | Built from | Reviewed |
|---|---|---|---|
| `synthetic_cover` | PM | `map_senate.json`: main Senate vs balance of power vs Senate × oil / Hormuz combos. Buckets {R} + {D or Other}, so Other is covered | yes (rules read 25 Oct) |
| `negrisk_set` | PM | gamma discovery: every open market in a negRisk event, placeholders and Other included | automatic; the set is incomplete if any leg is not accepting orders |
| `time_ladder` | PM | gamma discovery: same question at two deadlines; NO(by A) + YES(by B) pays ≥ $1 | **automatic, unreviewed**: alerts are suppressed until reviewed |
| `cross_venue` | PM + Kalshi | `map_senate.json` (2 pairs), `map_races.json` (35 candidate pairs, auto-matched by surname) | Senate: rules read. Races: Kalshi rules_primary read, PM wording not re-read per race |

Every cross-venue structure carries `divergence_loses_both = true` and its basis text (Kalshi pays on the President pro tempore on 1 Feb 2027 or on 4 of 8 media calls, and races pay on swearing-in; Polymarket pays on seats or the winner as elected). The two Senate pairs use disjoint ladders on both venues, so they never count the same liquidity twice. Profits are **per structure and not additive**: the Polymarket-only cover and the cross-venue pair can draw on the same Polymarket tokens.

## Phantom guards (`guards.py`, `persist.py`)
- **Crossed book** (best bid ≥ best ask) means the leg is rejected. This was the replay artefact in the sports work.
- **Stale book**: a venue timestamp or fetch older than 90 s means rejected. This was the stitched missing-hour books in the rescan audit. Kalshi gives no book timestamp, so its fetch time is used.
- **Incomplete set**: a placeholder or Other leg not accepting orders means rejected (the AL-04 one-live-candidate case).
- **Profit floor** of $5 at `min_edge` 0.5c: the thin Hormuz 3-way, at $2.05, stays silent.
- **Persistence**: an alert opens only after 3 consecutive clean polls spanning ≥ 120 s, and closes on the first failing poll. Each open and close goes to `alerts.jsonl` with `first_seen`, `duration_s`, peak and last profit, cost, return, edge, and the instruments used. Every priced structure with profit > 0 also goes to `snapshots.jsonl`, so we learn how irregular these are.

## Tests (fixed before running; `python3 scanner/test_scanner.py`): 16/16 pass
G1 fee formulas by hand · G2 negRisk walk by hand (200 sets, $7.50) · G3 Kalshi bid→ask conversion · **G4a** reproduces this morning's cross-venue Senate figure $2,636.80 (independent script) · **G4b** main-market-only $894.55 · **G4c** Polymarket-only cover $58.21 strict (the report's $62.45 used main D YES, which leaves Other uncovered; the independent script restricted the same way gives $58.21) · G4d Kalshi structures not tradeable with `--venues pm` · G4e snapshot passes the guards · G5 crossed rejected · G6 stale rejected · G7 one-poll blip ignored, 3 polls over 120 s open · G8 incomplete set rejected · G9 thin set below floor · G10 log duration and peak correct · G11 time ladder by hand · G12 end-to-end dry run with a fake clock (Polymarket cover opens TRADEABLE, Kalshi pair opens ALERT-ONLY, both close).

Not yet run against live venues: this container is blocked from both venues, so `fetch_books()` and `discover()` are untested code.

## Cadence and cost (estimated)
- **Hot loop, every 60 s**: one `POST /books` for about 150 Polymarket tokens (Senate family, race pairs, discovered sets) and about 36 Kalshi `GET /orderbook`. That is about 1.2 MB/min, or about 1.8 GB/day. Kalshi is about 36 req/min against its 20 req/s basic limit. CPU is trivial; RSS is under 100 MB.
- **Discovery, every 6 h**: gamma keyset pages for the `midterms` and `politics` tags at about 5 MB per 100 events, so about 100 MB per pass and about 400 MB/day.
- **Logs**: about 10 MB/day of snapshots, and alerts are tiny.
- **v2** (if v1 passes): switch the Polymarket hot loop to the market websocket. Bandwidth falls by roughly 10×, and alert durations get second resolution instead of minute resolution.

## Run
```
python3 scanner/run.py --minutes 2880 --poll 60 --venues pm --log reports/scanner/alerts.jsonl --snapshots reports/scanner/snapshots.jsonl
```
It needs a host that reaches clob.polymarket.com, gamma-api.polymarket.com and api.elections.kalshi.com (the server or a laptop). It uses the standard library only.

## First discovery check (25 Oct snapshot of 200 midterm events)
`screen_negrisk` finds **0** buyable negRisk sets. Midterm events are augmented negRisk, and their placeholder legs ("Party A…", "Other") cost $1 or have no asks, so a strict buy-all set can never come in under $1. The single-venue edge in politics is the synthetic cover, not the plain set. `auto_ladders` finds 0 in this sample. Pass `--tags` with other categories (for example `sports,crypto,economics`) to look for plain sets and ladders on newer non-augmented markets. That costs about 5 MB per 100 events per pass.
