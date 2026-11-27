# Will-say live nowcast: reprice-window scorer (spec v1.1)

Spec: `../specs/SPEC-will-say-live-nowcast-2026-11-25.md`. The v1.1 amendment explains why the scorer uses trade prints and not P121 books.

| File | Purpose |
|---|---|
| `nowcast.py` | Scorer: W bracket [W_lb, W_ub], $ floor at L in {1, 2, 5, 10, 30} s net of the 250 ms hold, placebo (MC type 1), plants (MC type 2), per-sub-family verdict |
| `test_nowcast.py` | 10 tests, all OK on 25 Nov: bracket, hold boundary, leak, fee threshold, sells and other tokens ignored, stale plant recovered (W 2.75-3.25 s, $50 at L=1), hold plant gives $0, a scorer with a drifted hold fails the plant, verdict cases, no pooling |
| `pull.py` | Builds the scorer input from `words.json` (from webb T112), using Data API v2 taker trades. Condition is asserted on every row; the page cap is reported, not silently cut |

## Run on Prime (R-039), after T112 is accepted
```
python3 -I pull.py words.json fee_rates.json input.json
python3 -I nowcast.py input.json > RESULT.json
```
