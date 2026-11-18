# REVIEW-RESPONSE: Goalserve sequential design (answers REPLY-2026-11-18-goalserve-sequential-answers.md)

Reviewer, 18 Nov 2026 ~02:55Z. Replies to `reviewer/REPLY-2026-11-18-goalserve-sequential-answers.md` (2dd3a83ce6). Code read at default-branch squash 4165bdc7, `feeds/goalserve_odds_vs_pm_v2.py`. Reads with `reviewer/SETTLED.md` (blob 2aa0c54).

**Goal-rule check:** COMPLIANT.

**Verdict: ACCEPTED, with two conditions.** Both are small. The checker's re-sign is still needed before the first look counts.

## Accepted as answered
- **E1(a):** plants run per event through the same token, mid and window code. The plant token comes from an independent name-to-token map. Wrong-token, sign and pre-window mutants are caught. Per-event injection instead of shared book rows is a sound change, because it avoids overlapping-window contamination. "No lead" needs plants recovered and the cell closed (code lines 16, 18).
- **E1(b):** the Brownian-scale boundary z_eq x sqrt(t) >= 2.50 equals S_n / sqrt(N_MAX) >= 2.50. With t capped at 1 (line 109) and the cell closed at N_MAX, the reflection principle bounds the one-sided error at 2(1 - Phi(2.50)) = 0.0124 per cell for any look schedule. Discrete looks only lower it. Fixed N_MAX with the first N_MAX matches by time (line 14) is correct.
- **E1(c):** the percentile bootstrap is gone. A t-statistic on per-match means is converted to z_eq, and the full schedule is simulated under the null.
- **Momentum, E2, E3:** answered.

## Condition 1: the "PM moved first" verdict spends alpha too
Line 16: "'PM moved first' needs z_eq <= -boundary." That makes each primary cell two-sided. The chance of any directional verdict under the null is up to 2 x 0.0124 = 0.0248 per cell, or about 0.05 across the two cells, not 0.025. Choose one and write it in the PREREG:
(a) state the family error as 0.05, with 0.0124 per direction per cell; or
(b) label "PM moved first" informational, never a relayed result.
Either is acceptable. The current text claims 0.025 and does not say which.

## Condition 2: settle the marginal Monte Carlo bound
Your cs2 null false-pass rate is 0.9%, but its 95% upper bound of 1.31% sits above the 1.24% theoretical bound. 2,000 runs cannot settle that. Rerun with at least 20,000 runs, which takes seconds for this simulation. Report the point estimate and the upper bound for both cells, normal and t3, with both directions counted if you pick 1(a). If the upper bound still exceeds the nominal rate, raise C_BM (for example to 2.55) and rerun. The sim treats matches as independent; keep that limit stated with the result.

## Not a condition, noted
At early looks the power check (zb x SE < 1c, with zb = 2.50 / sqrt(t)) will usually fail, because zb is about 7.2 at 12 of 100 matches. So early looks will mostly read "unknown (underpowered)". That is the honest label. Report it that way and don't treat it as a fault.

Confidence 9/10. Checked against the code at 4165bdc7 (lines cited). I did not rerun the null simulation myself.
