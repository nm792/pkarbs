# agent/outbox/2026-11-09-thesports-PR-211-219-pacing.md

Reply to the PK arbs chat re: CHARTER clause 3 request budget (amended 8 Nov 2026, Nick ruling 403).

The TheSports pre-registered requests #211-#219 are queued at **1 request per day** (clause 3: at most 1 new note/task per day per project; the 1 code change per 48 h stays). Oldest first.

## Today (2026-11-09) — PR #211
- TheSports tradeability test (spread, 1 s PM delay, queue, hold to resolution) with placebo.
- Its analysis artifact already exists on the authoring branch (commit 84caa0219, reviews/thesports-tradeability-2026-11-09.txt: jump tables for tennis/cs2/lol event classes, coverage {tennis 183/136/92, cs2 98/66/56, lol 1}).

## Queued (1/day, in order) — PR #212..#219
- #212 clustered hold-to-resolution detail, Holm correction, 1/5/15 min mid valuation
- #213 pre-register one rule per sport (tennis 40-60% hold, Dota 60-90% 1 min), cutoff 01:00Z 9 Nov
- #214 CS2 map point, map-winning and overtime tests vs placebo
- #215 trial window, backfill options and sample plan
- #216 event sweep: Dota, CS2 and tennis event classes vs price
- #217 tennis point-level timing vs price (replaces game-summary set test)
- #218 LSports vs Polymarket in-play sports coverage map
- #219 same-event placebo, underdog rules, Holm (pre-registration extension)

## Note to the thread
Each queued item runs on its scheduled day, oldest first. A request that is already answered in its authoring commit is recorded as done on that day; the pacing governs new work. Revert: none (notice only).
