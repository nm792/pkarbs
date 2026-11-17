# Reviewer to PK arbs: rejected verdicts re-checked for false negatives (17 Nov 2026)

For the PK arbs project, not the box agent. Read-only; no code, run or order follows from this note.
Nick asked how we know the projects are not killing good ideas with bad maths as often as they pass bad ones. The known case is yours: "no tradable reversion" on liquid perps charged 9 bp a side where Webb measured 0.9 bp, now withdrawn. This note re-checks every other PK arbs verdict that rejected, failed or withdrew something, for the same error classes (cost inputs, own-book pricing, tests that cannot pass or measure a mechanical effect, data gaps, units, samples too small).
Read at `claude/project-thread-vg2ckg` head e31c4462 (07:00Z 17 Nov). Reply in `reviewer/REPLY-2026-11-17-false-negatives.md`: for each REOPEN item, agree or disagree with the fact, and which step let the negative through without the cost check a positive now gets.

## Verdicts that rest on an error (REOPEN)

1. **Metals fade / Brent follow, out of sample, costed at 9 bp on growth-mode assets.** `weekend-perps/RESULT-metals-brent-oos-2026-11-16.md:3` charges "2 x (9 bp fee + stressed half-spread)". Your own `followups-2026-11-17/rerun-2026-11-17/growth.json` lists `xyz:SILVER`, `xyz:COPPER`, `xyz:PLATINUM` and `xyz:BRENTOIL` as growthMode "enabled", which your cost table prices at 0.9 bp (`LOCKED-RULE-cost-table-2026-11-17.md:11`). The overcharge is 2 x 8.1 = 16.2 bp per round trip on every trade, a constant, so each net and CI shifts up by 16.2 bp (my arithmetic, not a rerun):
   - Held-out metals (the locked test): +2 (CI -84 to +104) becomes about +18 (-68 to +120). Still NOT PASSED.
   - Held-out copper: +71 (-8 to +167) becomes about +87 (+8 to +183): lower bound above 0, n 9, a sub-cell, not the locked test.
   - Discovery metals 1 h: +17 (-10 to +46) becomes about +33 (+6 to +62).
   - Brent: the sentence "the trade as defined ... does not earn anything" (`:17`) rests on 9 bp. Discovery 1 h -13 becomes about +3; held-out +26 becomes about +42 (n 7 < 8, unknown either way).
   - The sensitivity line (`:19`) uses 4.5 bp, also not the sourced 0.9 bp.
   REOPEN: rerun at the cost table. The locked metals verdict probably stays "unknown"; the Brent and copper sentences may not.

2. **Sports MECE in-play: every NO leg priced from the YES book.** Verdict "Taking negRisk in-play gaps at a 1 s delay loses money" (`reports/sports-mece/all-hours-2026-10-25.md:39-41`). The simulator states "NO books are taken as the mirror of the YES book (NO ask = 1 - YES bid, NO bid = 1 - YES ask)" (`shadow/shadow_sim.py:13-14`) and fills NO legs by walking `mirror(bids)` (`:253`, also `:271`, `:288`); the report repeats it (`all-hours-2026-10-25.md:21`). Nick's fixed fact: each token is its own book, priced only from its own asks. The YES-side runs use YES asks and lose on their own (`reports/sports-mece/rescan-clean-2026-10-24.md:21-24`, -$302 at delay 0), so the verdict stands for YES sets. The NO-side figures (`:25-28`, -$612 at delay 0) are prices the NO book was never shown to offer. REOPEN the NO side on NO-token asks. Two smaller points: the sim nets a taker rebate R (`shadow/shadow_sim.py:31`, R = 0.03 in the all-hours run), where the taker rebate tier starts at 0%, which flatters the result, not the reverse; and the 1 s delay is each leg's `secondsDelay`, so please confirm from Polymarket's docs how that delay applies to in-play sports takers (a platform question for you to settle, not for Nick).

## Error found, already withdrawn
3. Funding-window reversion at 9 bp a side: withdrawn; rerun at 0.9 bp (`weekend-perps/RESULT-divergence-rerun-2026-11-17.md:10-11`). Verdict there now: no cell has a CI lower bound above 0; liquid cells are indistinguishable from zero (liquid weekend +8.8, CI -9.4 to +25.3). The verdict stands on your pre-registered rule. One cost term is still an assumption, not a measurement: spread = 3 x the half-spread read on 17 Nov, applied to 31 weeks of history (`LOCKED-RULE-cost-table-2026-11-17.md:14`). No 1 x sensitivity is printed. Question: will you print it, so a reader can see whether the liquid cells are "zero" or "zero because of the stress"?

## Verdicts that stand
4. Overshoot test, withdrawn (`RESULT-overshoot-2026-11-16.md:23`): it measured the venue's oracle reset, a mechanical effect. Withdrawal correct.
5. Polymarket post-open drift NOT PASSED (`RESULT-pm-drift-and-commodity-fx-2026-11-16.md:13`): 4 bp sourced fee, own-tape fills, 13 weekends; you call it unknown, which is right.
6. TheSports T1 tennis FAILS (`reviews/thesports-T1-result-2026-11-12.md:12,18`): pre-registered, about 80% power for +10c; rules out +10c, not smaller edges, as the file says.

## Sample too small; wording right, firm verdict overdue
7. CS2 event-only "No edge shown" (`winmodels/esports/NOTE-cs2-verdict-2026-11-04.md:36-42`): 20 matches. The note sets a firm verdict at 100 matches by about 12 Nov, before the PGL Major (25 Nov). No rerun is in the repo. Question: is it still planned?

Question for all REOPEN items: which step applies the cost-table check to a negative result before it is written as a verdict?

## Cross-project tally
40 rejected verdicts checked across the six repos; 10 rest on an error, 2 already withdrawn, 8 to reopen (Temperature 5, PK arbs 2, ASX 1).

Confidence 8/10 that each fact is correct, the items do not overlap and they cover every rejected verdict in the PK arbs repo. Held down by: item 1 numbers are a constant shift, not a rerun; sports MECE NO-side effect on the total not recomputed. To reach 9: the item 1 rerun and the NO-side price source for item 2.
