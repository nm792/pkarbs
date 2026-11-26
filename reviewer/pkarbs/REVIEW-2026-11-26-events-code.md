# Review: PK events-trading code pushed 26 Nov 03:58-04:27Z (pkarbs `reviewer`)

Reviewer, 26 Nov 05:40Z. Read against:
- the specs (SPEC-macro-pickoff-paper-2026-11-24, the earnings-beat README, SPEC-will-say-family);
- DECISIONS M46 (the forward-test definition) and G68 (Nautilus only, no transformation);
- R-039 (backtests on Prime);
- SETTLED A1/A3/A6;
- INSIGHTS I-18 and I-46.

I ran every test here in the container (code tests only): **all pass.**

| Commit | What | Tests (run here) | Verdict |
|---|---|---|---|
| fdc6d9fe5b + 0096568cbb | `metric-pickoff-2026-11-26/`: stale-ask pickoff scan on prints over 1,034 events / 8,073 markets, in 21 families | test_scan.py ALL PLANTED CHECKS PASS (it needs the folder on sys.path: `python3 -I` alone fails to import `scan`) | **Accept as an evidence screen** (FLOOR, prints only), with 5 defects below |
| 867749543a | `it/mentions_p121_report.py` (P147 report on the P121 decisions) + `it/mentions_beat_forward_list.py` (earnings-beat daily list of open markets with a YES own ask < 50c) | 15/15 and 4/4 PASS. Each test needs the target file passed as argv[1] | **Accept** |
| dd7134a6cb + 11c66ea87a | `it/macro_latency/`: per-fill latency table explaining why the PCE evidence P&L rises from 0.5 s to 5 s, plus make_winners.py | 4/4 and 9/9 PASS. Its macro_pickoff_score.py is byte-identical to `it/macro_pickoff_score.py` (checked) | **Accept**. IT runs it on Prime |
| f366b685c0 | IT row P166: PandaScore v4 live read + deploy by 08:00Z | n/a (instructions) | Accept |

## Defects (numbered; none blocks use as evidence)
1. **A 62 MB binary is committed to git** (`metric-pickoff-2026-11-26/raw-inputs.tgz`, 0096568cbb). It sits in history for every clone. Move it to the box or the project folder, and keep only a pointer and sha256 in git. Removing it from history is a rewrite, so that is Nick's call; going forward, add `*.tgz` to that folder's `.gitignore`.
2. **The scan ran in the container**, not on Prime (R-039: backtests on Prime). It is a public-prints screen, the same class as my earnings screen, which carries the same flag. Rerun on Prime before any figure is used beyond ranking.
3. **Fee not deducted** (stated in the README). Macro rate 0.01 gives at most 0.25c/share, so the effect is small on calendar rows. Deduct the market's own feeSchedule in the rerun.
4. **Silent truncation risk:** `fetch_trades` stops at 30 pages (15,000 taker rows) or at a price heuristic. For busy markets the release window can fall outside that, and the row then reads as "no prints". Log a `complete` flag per market, as `will-say-nowcast/pull.py` does.
5. **ONSET rows are hindsight** (R = the jump itself). The README already labels them NOT a floor; keep them out of any $/day total. Elections at $296/day is 70% one event.

## Rule checks
- **Own-token books (A1):** pass. Winner-token BUY prints only, YES and NO kept separate, loser token rejected (planted).
- **Forward test (M46) and Nautilus only (G68):** none of this code produces a strategy result.
  - The scan and the latency table are evidence tools.
  - The P121 report prints the logger's own decisions and labels the KEEP_THRESHOLD "on" variant as a post-hoc reprice, with "on-only unobservable" never invented.
  - Consequence: the PCE "+$29.60 / +$43.12" figures are **evidence-tool output, not a SIM or a forward-test result**. STRATEGY.md and INSIGHTS I-46 are corrected to say so. The PK thread made the same correction (P-WATCH-21).
- **Never stage orders (A6):** the README's "Preloaded orders" section is docs research only. No signing or order code exists. Any preload implementation is order staging and needs Nick plus a Nautilus node.
- **Taker hold (A3):** the README re-reads `seconds_delay` per market and refuses if unknown. Pass.

## What it changes in STRATEGY.md
- Row 7 (macro pickoff) gains the calendar cells ranked by the scan: CPI + eggs, jobs, GDP, Fed. Next captures: jobs 4 Dec, FOMC 9 Dec, CPI 10 Dec.
- Row 3 (earnings-beat) gains the daily forward list.
- New row 16: ONSET event families (tweets, launches, announcements, elections, box office). Each is UNPROVEN until it has a named trigger feed.

Confidence 8/10. To reach 9: a Prime rerun with fees and completeness flags.
