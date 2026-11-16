APPROVALS NEEDED: none. Read-only analysis; no code, collector, or live process changed.

RESULT — sim on real data
- Reran the 09:45 adapter-corrected runner (SHA-256 `fbe4baf5ac6fa9a6df2a94c49ef254e318673723b9ce8e353b39f192667636b7`) against the full available PS capture in the historical source directory and its paired PM capture. Run exited 0 in 12.72 s; peak RSS 88,416 KiB. Synthetic test provenance is in the 09:45 note; this execution itself is on real data.
- Setup check: 23 PS matches in the historical source; the runner and an independent recount both find 1,911 counter increases. Exact normalized-name PM join on 18; five unmatched names are listed below. PM books: 520,905 rows. Median `ms - sent` is 156 ms (P90 422 ms; observed range 52–8,571 ms), consistent with a shared capture clock but including recorder delivery delay. PS time uses local `recv_ns`; `updated_at` is not used.
- The three-event sample table was computed from the same PM capture. The PM mid shown is the exact event-side outcome token at the nearest book row before and after the feed receive timestamp.

| game | match / market | event | PS receive UTC | PM mid before | PM mid after |
|---|---|---|---|---:|---:|
| Dota 2 | Team Liquid vs LGD Gaming — Game 1 Winner | LGD Gaming +1 kill | 17:06:45.864Z | 0.0245 at 17:06:44.990Z | 0.0245 at 17:06:46.015Z |
| CS2 | STATE vs BBL — Map 2 Winner | STATE +1 round | 17:06:56.111Z | 0.5000 at 17:06:54.983Z | 0.5000 at 17:06:56.996Z |
| Dota 2 | Team Allied vs potn9ki — Game 2 Winner | Team Allied +1 kill | 17:08:33.327Z | 0.4600 at 17:08:33.074Z | 0.4600 at 17:08:34.156Z |

The feed-relative data window starts at 17:06Z; the aligned PM books begin at 17:06:10.976Z. The three samples above are after that point. The runner was executed on the complete historical source directory, not hand-selected PS rows.

Cells from the runner, pasted as calculated. Leads are seconds; positive means the first qualifying PM move came after the feed. `n` is PS events; placebo count is 10 per included match/series where available.

| title | series | stratum | n events | n matches | real onset % | placebo onset % | median real lead | median placebo lead | diff | 95% match-bootstrap CI | price after feed % | verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| cs2 | map | all | 424 | 10 | 70.8 | 8.0 | -30.62 | 23.24 | -53.86 | [-64.22, -25.20] | 11.7 | no lead (needs audit) |
| cs2 | map | <25k | 288 | 7 | 59.4 | 4.3 | -28.30 | 31.29 | -59.58 | [-67.79, -21.67] | 17.0 | no lead (needs audit) |
| cs2 | map | >=25k | 136 | 3 | 94.9 | 16.7 | -33.30 | 15.75 | -49.05 | [-50.10, -34.81] | 4.7 | no lead (needs audit) |
| cs2 | match | all | 528 | 10 | 62.1 | 18.0 | -29.02 | 28.40 | -57.42 | [-77.13, -43.00] | 12.5 | no lead (needs audit) |
| cs2 | match | <25k | 356 | 6 | 53.1 | 15.0 | -31.51 | 28.19 | -59.70 | [-61.66, 1.78] | 13.2 | no lead (needs audit) |
| cs2 | match | >=25k | 172 | 4 | 80.8 | 22.5 | -27.04 | 33.05 | -60.08 | [-81.84, -45.14] | 11.5 | no lead (needs audit) |
| dota2 | map | all | 979 | 8 | 48.2 | 9.7 | -22.69 | -31.99 | 9.30 | [-66.57, 28.83] | 24.2 | no lead (needs audit) |
| dota2 | map | <25k | 956 | 7 | 48.0 | 8.6 | -23.48 | -15.89 | -7.58 | [-78.83, 14.61] | 24.2 | no lead (needs audit) |
| dota2 | map | >=25k | 23 | 1 | 56.5 | 50.0 | -8.58 | -49.37 | 40.79 | [40.79, 40.79] | 23.1 | unknown (n=23 < 30), preliminary |
| dota2 | match | all | 1,114 | 8 | 42.3 | 5.7 | -14.14 | -47.96 | 33.82 | [-4.55, 39.14] | 30.8 | no lead (needs audit) |
| dota2 | match | <25k | 1,091 | 7 | 42.4 | 5.7 | -14.83 | -47.96 | 33.13 | [-5.66, 38.61] | 30.2 | no lead (needs audit) |
| dota2 | match | >=25k | 23 | 1 | 34.8 | — | 11.36 | — | — | — | 62.5 | unknown (n=23 < 30), preliminary |

The <25k / >=25k mapping is from the archived volume file supplied to the corrected runner. These labels are conditional on that volume file and its capture window; the runner output is not an independent audit. No pass/fail claim is made. The table does not satisfy the Standard's minimum sample per stratum for Dota >=25k.

- Prior recount comparison: PS rows used by this runner contain 598 CS2 round increases versus 702 in the Nov 14 recount (-14.8%); Dota increases are kills 989 vs 1,069 (-7.5%), towers 223 vs 243 (-8.2%), barracks 68 vs 76 (-10.5%), Roshan 33 vs 38 (-13.2%). These exceed the note's 5% tolerance. The comparison remains unresolved; treat the cells as preliminary, not the pre-registered full-window result.
- The independent event-count recomputation confirms the runner: 1,911 counter increases across 23 PS match IDs (CS2 rounds 598; Dota kills 989, towers 223, barracks 68, Roshan 33). It is below the 14 Nov recount (CS2 702; Dota 1,069/243/76/38) by 14.8%, 7.5%, 8.2%, 10.5%, and 13.2%, respectively. The difference exceeds the note’s 5% tolerance; it is not reconciled, so the counts and cells remain preliminary.
- The 09:45 note requested a separate `/vol2/pkarbs/pandascore/raw` run if the historical directory lacks the full 13–14 Nov span. Its current raw directory contains only a later 15 Nov file; no comparable 13–14 Nov continuation is available there. The result therefore does not combine later raw capture with the historical sample.
- Five exact-name PM unmatched matches: Apogee Esports vs Leo Team; BAKS Esports vs EX-Zero Tenacity; Hype Tech vs Phantom; Inner Circle x Insanity vs Nemiga Gaming; PARIVISION vs Yellow Submarine.

OPEN / NOT VERIFIED
- Independent audit required by STANDARD v1 section 4 has not run; no pass/fail conclusion is available.
- The 13 Nov 17:06Z+ market-volume source used for strata and actual registered match volumes must be audited independently.

DATA
- Reproducible result JSON: `/vol2/pkarbs/scratch/ps-lead-20261115/result-final-20261116.json`.
- Historical-only rerun JSON: `/vol2/pkarbs/scratch/ps-lead-20261115/result-historical-final-20261116.json` (same 23-match dataset; separate PM capture root gives different bootstrap placebo draws, not a second independent sample).
- Setup rows, source counts, run log and `/usr/bin/time -v` output are in `/vol2/pkarbs/scratch/ps-lead-20261115/`.

Count: 1,911 events confirmed by an independent recount; 23 match IDs, 18 matched, five unmatched; 12 cells. One read-only bounded run; 88,416 KiB peak RSS; no spawned process left running.
