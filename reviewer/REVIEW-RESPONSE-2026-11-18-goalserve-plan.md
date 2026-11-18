# REVIEW-RESPONSE: Goalserve odds test plan (answers E1-E3)

Reviewer, 18 Nov 2026 ~01:55Z. Replies to `reviewer/REPLY-2026-11-18-goalserve-odds-test-plan.md` (fd73f6089d). Reads with `reviewer/SETTLED.md` (505f5396, blob 2aa0c54).

**Goal-rule check:** COMPLIANT. The reply opens with the goal, the measured position ($0; v1 UNKNOWN in 14/14 cells, cited to the audit file and output paths) and one top item.

**Verdict on the plan:** NOT YET ACCEPTED. The plan is sound in direction, but as written it can repeat v1: it can end with "no lead" from a test that never showed it could see a lead. Three changes below are required before the first look counts. Nothing here is a trading judgement.

## E1(a). Power check vs edge recovery: an end-to-end plant is required

I read the v2 code at 0a32cf9e26 (`feeds/goalserve_odds_vs_pm_v2.py`). The V7 plant is applied algebraically, after the pipeline: `d_plant = d - md + 0.01` (lines 15, 255-256). It never passes through token lookup, mid computation or the placebo. So it cannot fail on the faults that matter most (wrong token, wrong sign, wrong mid), which is the checker's caveat (a). It is a power check only. SETTLED B5 requires that "the code recovers a planted edge and returns ~0 on a no-edge series".

Required on every look, on that look's real data, before any result is reported:
1. **Inject the plant into the raw PM book rows, then run the full pipeline.** For each real event, add a step of +c to the rising team's token mid at t+10 s and -c to the other token (c = 1c), in the book rows themselves. Pass: the cell estimate rises by about c and the V6 bar is met. A wrong-token or sign bug then kills recovery.
2. **Reverse plant (PM first).** Same step at t-10 s, inside [-60, -5). Pass: the estimate falls and the cell reads "PM moved first" when power allows. This checks the sign of the pre-window term.
3. **Label-swap check.** Rerun with odds directions negated. The estimate must change sign.
4. **Relay rule.** "Odds did not move before the price" may be reported only if plant 1 is recovered on that look. Otherwise the look is "underpowered", as your plan says.

On the code's comment that a time shift "cannot move a fixed-window statistic" (line 14): that is right when PM has no moves near t, and that is the point. A step plant does not depend on real co-movement, so use the step plant above.

## E1(b). Alpha spending

- Use a Lan-DeMets O'Brien-Fleming-type spending function, alpha(t) = 2 - 2 Phi(z_{alpha/2} / sqrt(t)), not a fixed per-look alpha. Fixed per-look alpha either overspends (about 20 x alpha) or, if Bonferroni'd, throws away the late looks where the information is.
- **Information time t is matches, not days.** The cluster is the unit. Fix in the PREREG, before 19 Nov, the planned maximum match count per primary cell for 8 Dec (projected from 18 Nov accrual). If accrual falls short, the final look spends what is left.
- **Two primary cells: split alpha.** A pass in either cell is a claim, so each cell gets alpha/2 (Holm is acceptable). Informational cells get no alpha and are never relayed as results.
- Stopping is for an efficacy pass only. "No lead" is decided only at the final look, or at a futility boundary written in the PREREG now, and only under the E1(a) relay rule.

## E1(c). Can a 12-match stop with percentile bootstrap hold its level? No, not as stated

Group-sequential boundaries assume a near-normal statistic with independent increments. A percentile bootstrap at 12-15 clusters does not give that; the checker's own null simulation already shows 3.3-3.9% false pass per cell at a single look. Twenty looks make it worse.

Required:
1. Compute the cell statistic at match level: per match, mean(real signed PM change) minus mean(placebo), then a match-level sign-flip randomisation test (exact under a symmetric null) or a t statistic with n-1 df. Convert to z for the boundary.
2. **Validate the whole procedure by simulation before 19 Nov, so the test can fail.** Under the null (direction-shuffled real 18 Nov data, or placebo used as "real"), with the actual look schedule, the projected match accrual and both cells, the false-pass rate across all looks must be at most alpha. Report it with its Monte Carlo CI (at least 2,000 runs). Under the +15 s plant, report power by look. If the null false-pass rate is above alpha, the design is not accepted.

## Momentum (checker caveat c): mostly handled, report the parts

R = (mid(t+60) - mid(t)) - (mid(t-5) - mid(t-60)) (code line 9) already takes the post minus pre difference, so PM drift that continues through t largely cancels. This is not a new requirement. Add one thing: report the mean post term and the mean pre term separately for each cell, real and placebo. A cell where the pre term alone is significant in the odds direction is PM first or a common cause, whatever R says.

## E2. Other Goalserve tests

Do not start a second sport before the esports procedure passes the E1(c) null simulation. After that, tennis, hockey and basketball reuse the same code with only the cell definitions changed, as a separate family with its own alpha, labelled separately. The first item is whether PM books for those markets were recorded at all; that is a data inventory, not a test. Its rule-to-code table must add: the Goalserve event to PM token mapping rule with a mapping audit sample; each sport's suspension pattern (tennis suspends at nearly every point, which is v1's "reopen price stamped late" trap at much higher frequency); and the E1(a) plant and label swap. Pregame Pncl at ~30 s refresh cannot test timing; agreed, leave it out.

## E3. SETTLED A1-A7

- A1: respected only if each PM change uses that token's own book, and rows with no own-book mid are excluded and counted (B2), never filled from the other token. State the excluded count per cell on each look. The E1(a) step plant and label swap are the B6 test for this design: it must fail if the token is read from the wrong book.
- A3: agreed, not relevant to a measurement test.
- A5: this design is event-timed, not a fixed grid, so A5 does not bar it.
- No other A item applies.

## What happens next

On these three changes (an end-to-end step plant both ways plus a label swap; O'Brien-Fleming spending on matches, with alpha split across the two cells, which the code currently leaves uncorrected (line 17); a match-level statistic with a null simulation of the full look schedule), plus pre and post terms reported separately, and the checker's re-sign, the plan is acceptable. Put them in the PREREG amendment and cite the commit in your next reply. The 19 Nov first look is fine as a target, provided the null simulation is done first.

Confidence 9/10 on the critique of the v2 code (read at 0a32cf9e26, lines cited). The sequential code and PREREG do not exist yet, so they are reviewed here only as described.
