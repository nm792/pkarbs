SETTLED.md cited: reviewer/SETTLED.md at commit 505f539672cdcb39b640958e61c2f9e72c321fcc (blob 2aa0c54). Rules A1-A7 applied: every Goalserve/bet365 price below is compared with Polymarket's own token book, never NO = 1 - YES. Reviewer dir read 18 Nov ~02:20Z: no new REVIEW or DECISION file since 17 Nov.

# Reply: Goalserve odds test plan, put to the Reviewer for attack (18 Nov 2026)

**1. Project goal.** Find and build un-publicised, automated edges across prediction-market categories, target $500/day with no catastrophic loss.

**2. Where we measurably stand against it.** Goalserve has been a paid-feature trial for about six days (started ~12 Nov; Nick registered 12 Nov 13:10Z per feeds/NOTE-goalserve-trial-plan-2026-11-12.md). We have NO answer on whether Goalserve bet365 odds move before the Polymarket price. The only run so far (v1, 17 Nov ~17:40Z, code 1cb5c847, seed 20261117, 95 Goalserve files, 14,262 events, outputs agent/status/goalserve-odds-vs-pm-result-2026-11-17-shift{0,5,15,25}.json, head 6e05665c92) was audited UNKNOWN in all 14 cells (reviews/AUDIT-goalserve-odds-vs-pm-result-2026-11-17.md). Progress against $500/day from Goalserve: $0, nothing proven, nothing disproven.

**3. The single item that matters most.** Whether the new daily plan can silently repeat v1's failure, i.e. a test that cannot detect an edge and therefore returns UNKNOWN or a false "PM first". The plan below has one guard (a planted edge) that the checker itself says is only a POWER check, not an edge-recovery check. I ask you to attack that first.

## A. What v1 did and why it failed (all from the AUDIT file, not recomputed by me)
- Gate: placebo onsets needed in >= 30 matches; sample had 25 CS2, 12 Dota 2, 1 LoL, 4 unparsed matches. Unattainable whatever the data said. The checker admits it signed that amendment without checking it against match counts.
- Statistic: onset-based lead. Planted +25 s on the real series moved medians by +8, +4.6, +1.7, -1.0, -4.4 s (CS2 Match Winner -11.4 to -3.4 etc.). Plant not recovered, so signs and sizes say nothing about who moved first.
- Placebo not like-for-like: 4-19% placebo onset rate vs ~70% of real events; odds "event" fires ~100 times per match (2c jitter, suspend/reopen). 54% of 181,216 rows (98,148) were suspended winner-market rows, so many "events" are reopen prices stamped late by construction.
- Setup facts: Goalserve poll gap median 1.98 s, p90 2.09 s (not ~1 s); PM book cycle median 1.01 s, p90 4.06 s; bm field empty on all rows (bookmaker not identified in the data); 35% of events had no PM market.
- Label for v1: UNKNOWN. I withdraw nothing and relay no "no lead".

## B. v2 (rule-to-code signed)
- Code goalserve_odds_vs_pm_v2.py, PR #400 (371480a7), fixes PR #401 (0a32cf9e26). Checker "Audit CS2 model" (a project thread, not the author) signed all 22 rows MATCH at ~23:20Z 17 Nov (reviews/SIGNOFF-goalserve-odds-vs-pm-v2-rule-to-code-2026-11-17.md). Self test ALL PASS: +15 s 20/20 seeds, +10 s 20/20, no-edge false pass 0/20, PM-first reads "PM moved first", suspend/reopen trap events not counted, outage case 79 not 80 events.
- Design: time-aligned, non-onset. For each odds move while the market is open on both payloads, signed PM mid change over [-60,-5) and [0,+60) vs a direction-shuffled placebo (same t, random token, random sign), match-clustered bootstrap, per-match cap, primary cells fixed as cs2|Match Winner and dota2|Match Winner (others informational). Gate 12 matches per cell. Each token on its own book (A1).
- Conditions that travel with every run: omit --plant-c and --seed (checker verifies plant_c == 0.01 and seed recorded); poll logs supplied; outage rule clears baselines when poll gap > 10 s; another thread hand-checks the first 20 events of the biggest cell; ties_d_zero reported; wording only "odds moved before the price within the 60 s window" / "did not", never seconds; independent audit before relay; a "no lead detected" counts only if plant_detected is true.
- Checker's own caveats, which I repeat so you can weigh them: (a) the 1c check is algebraically "1.96 x SE of the cell mean < 1c", a power check; a sign flip or wrong token would still pass it, and the hand check is the only guard; (b) windows of 60 s cannot resolve a lead under ~5 s (Goalserve stamp up to ~2 s late, PM cycle up to ~4 s); (c) the placebo controls volatility, not momentum; (d) percentile bootstrap undercovers at few matches (checker's null simulation: false pass 3.3-3.9% per cell at 12-15 matches, ~33% chance of any false pass across ~10 cells, which is why only two cells can pass).

## C. New plan since Nick's request (18 Nov 01:40Z; thread cmsg_01Te5Ysv754GBskR25k8ZXLmWHMMF5WwgZVwGUnQaFxBri)
- The earlier plan (one run 25 Nov on 18-24 Nov data, slot in it/REPLY-2026-11-17-goalserve-E2-posted-slot-25Nov.md) is dropped: it wasted a free trial that ends ~12 Dec (estimate, not confirmed).
- Data: only 18 Nov 00:00Z onward (13-17 Nov already seen; a pass there does not count).
- Looks: one per day, 19 Nov to 8 Dec (20 looks), each on all data since 18 Nov, with alpha spent per look so early looks need a very large effect.
- Daily output: match count per primary cell; first look result as soon as either primary cell reaches 12 matches; and on every look, whether a planted edge on that day's real data was recovered. If not recovered, the result is reported at once as "underpowered", not as a verdict.
- Status at this writing: the sequential rule, code, self test and PREREG amendment are NOT yet written or merged, the checker has NOT re-signed it, and IT has NOT confirmed a daily slot. Nothing has run on 18 Nov data. First look target 19 Nov, labelled a target.
- Other testable items: tennis, hockey, basketball in-play odds are stored since the store-all install (P15b/026be71f), the same test could run on them if PM recorder books exist for those markets (unknown; IT inventory to be requested). Pregame Pncl (~30 s refresh) cannot show a timing lead, not a latency test. A value-vs-price test is a different question and is not started.

## D. Honest timeline and why there is no answer yet
Facts with sources; items marked (memory) are from project notes and I did not re-open the primary file.
- 12 Nov: trial found, locked test written and merged (PR #274, #276); my first plan wrongly assumed Pinnacle in-play, corrected 13:10Z to bet365 only, WebSocket not for esports/cricket/rugby, esports score feed 1 min (feeds/NOTE-goalserve-trial-plan-2026-11-12.md). v2 task PR #284.
- 12-13 Nov: key not installed for ~14 h because the box agent never read Nick's message; escalated to IT (PR #286, issue #282); key and IP checks passed 13 Nov 02:19-02:25Z; first poller 02:38Z covered tennis, soccer, baseball, NHL only. My error: I never asked for esports in that first capture. Esports capture live 13 Nov ~14:04Z, payloads from ~15:09Z (memory).
- 13-16 Nov: capture ran, but no lead test was run on it. Goalserve odds v1 first ran 17 Nov, i.e. four days after capture started. My share: I locked tests but did not insist on a deadline-bound run; the harness-first rule (Nick 16 Nov) and the fixed-grid lessons slowed it; I did not escalate the store-all/root-disk issue until 17 Nov (it/IT-2026-11-17-root-disk-p15b-no-token.md).
- 17 Nov: P15b store-all install and chunk D (code 1cb5c847, PR #397/#398) ran; v1 result ~17:40Z; audit UNKNOWN; Nick approved the stricter rerun 22:15Z; v2 signed 23:20Z.
- Causes: (1) my plans set slow dates (25 Nov); (2) the test needed three rewrites because of gate and placebo errors that the checker and I both signed; (3) IT/box dependencies each took half a day or more; (4) 13-16 Nov raw files exist only on the box (ship_raw.sh deletes hour files after 90 min), so they cannot be re-audited from here. Of these, 1 and 2 are mine.
- Unknown: exact trial end date (Goalserve never confirmed; estimate ~12 Dec).

## E. Questions to the Reviewer
1. Can the daily sequential design repeat v1's failure? In particular: (a) is a power-only planted 1c check enough to separate "no lead" from "cannot see a lead", or do you want an edge-recovery plant (shift of PM or of odds timestamps by a known lag) before any "no lead" is relayed; (b) alpha spending across 20 correlated looks on a growing sample, which spending function would you accept (O'Brien-Fleming style vs fixed per look), and with 2 primary cells do we split alpha across them; (c) can a stopping rule at 12 matches per cell, with match-clustered bootstrap, hold its level?
2. What else in the Goalserve trial should be tested now that is not a duplicate of this test, given bet365 only for in-play, Pncl pregame only, no cricket/rugby odds? Specifically: is a test of bet365 odds vs PM on tennis/hockey/basketball worth starting before the esports first look, and what must its rule-to-code table contain?
3. Anything in A1-A7 that this design breaks: e.g. A1 (own-book pricing) is respected by token-own-book PM change; A3 (taker hold, scope question open) matters only if we later trade.

I will relay your answer to Nick's coordinator the moment a file appears in reviewer/. Next check of this branch: every 30 min.

Confidence 7/10. Reasons below 9: (i) the sequential rule and code do not exist yet, so I cannot show it is safe; (ii) v1 numbers are from the checker's audit, not recomputed by me (raw data on the box); (iii) the 13-16 Nov timeline details marked (memory) were not re-read. To reach 9: the merged sequential PREREG with its self test, the checker's re-sign, IT's slot confirmation, and your answer to E1.
