# from_agent/thesports-books-coverage-2026-11-07.md — why chunk 32295 recorded few markets + widening ask (code-gated)

**Approvals needed:** 1 consent-gated item awaits the next interactive session — widening the capture's book scope to include every CS2 "Map N Winner" market is a code edit to `live/thesports/capture.py` (the discovery filter). Not applied here; recorded for the tap.

## RESULT
- **Measured cause (chunk 32295, 04:00Z–~08:00Z 7 Nov):** the capture's Polymarket discovery found only **12 tennis moneyline markets = 24 tokens** total, and stayed there the whole chunk (max `discover_pm` tokens=24 across 16 discoveries). `books_mid.jsonl.gz` holds 30,830 rows, all from those 24 tokens — so it is **not** a dropped/truncated capture; the discovery itself never saw more.
- **Exact settings, from `live/thesports/capture.py` (origin vg2ckg):**
  - `MKT_TYPES = (None, 'moneyline', 'child_moneyline')` — the filter records **only** plain moneyline/child-moneyline markets. CS2 "Map N Winner", spreads, totals, and outrights are **excluded by this line** (`if m.get('sportsMarketType') not in MKT_TYPES: continue`). This is why no CS2 markets appear at all.
  - Live window rule: a market is kept only if `start within [20 min before, 6 h after]` discovery time (`st - 1200 <= now <= st + 6*3600`).
  - `--sports` default = `tennis,lol,cs2,dota2,nba,nfl,cricket` (all six are enabled), so the small set is not a sport-scope miss — it is the MKT_TYPES moneyline-only filter plus the live-window, and at 04:00-08:00Z only tennis had in-window moneyline/child_moneyline events on Polymarket.
- **Comparison to chunk 8917:** that chunk recorded CS2 "Map N Winner" books because its market set (per TASK-thesports-trial scope) was captured when CS2 Map-Winner moneyline events were live and in-window; the 32295 window had none live, and even if one had been, MKT_TYPES would still exclude non-(child-)moneyline types. The two are consistent once the filter is read.
- **Keep everything, delete nothing:** confirmed — no TheSports/PM book capture (raw or slim, incl. ts_mqtt, books, pmws, markets, log) is deleted or overwritten; the 32295 slim commit (2a497fa9) is intact and the 2 h export cadence continues.

## DATA
- `rn1/scores/thesports/slim-0517-32295/{markets,books_mid,log,counts}.jsonl*` — 12 markets / 24 tokens discovered; 30,830 book rows.
- `live/thesports/capture.py` — `MKT_TYPES` (line 45) and discovery filter (lines 156, 162).

## OPEN / NOT VERIFIED
- Widening the exporter to include CS2 "Map N Winner" (and any non-moneyline game-winner the thread wants) = edit `MKT_TYPES`/filter in capture.py and add it to the next export — **code change, consent-gated**, waits for the tap.
- Whether Polymarket carried live CS2 Map-Winner events during 04:00-08:00Z 7 Nov — not re-scanned retroactively; the "none in-window" reading is from the discovery log, not an independent event query.

Count: notes run 1 (books-coverage diagnosis), outstanding 1 (future CS2 Map-Winner widening), PENDING open 1 (capture.py edit tap).
Context: chunk 32295 book-inventory gap explained by MKT_TYPES moneyline-only filter + live-window discovery; CS2 books need a gated capture.py scope edit.
