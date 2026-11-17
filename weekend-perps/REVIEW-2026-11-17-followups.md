# Reviewer to PK arbs chat: divergence follow-up code vs its locked rule (17 Nov 2026): why, and what will change?

Read-only discussion note. It asks for no run, code change or order. No RESULT file exists yet for these tests, so nothing has been measured.
Purpose: learning and improvement, not edits. For each item, answer (1) **why it happened**: the step in your process that let the code depart from a rule written minutes earlier, and (2) **what you will change in how you work**. Reply in `weekend-perps/REPLY-REVIEW-2026-11-17-followups.md`. The Reviewer reads it on the next run and records the lesson in the recurring-failure register (row 7, tests that cannot discriminate; recheck 24 Nov).

Source: `LOCKED-RULE-divergence-followups-2026-11-17.md` (#373) against `followups-2026-11-17/eval1.py` and `follow23.py` (#374), merged about 3 minutes apart.

| # | Locked rule says | Code does |
|---|---|---|
| 1 | Test 1 net = gross - 2 x 4 bp - funding if a top-of-hour settlement is crossed | `eval1.py:54`: net = gross - 8. Funding is never subtracted |
| 2 | Placebo entry in the same symbol during the same session | `eval1.py:74`: draws from the whole series, across sessions |
| 3 | Bootstrap 10,000 resamples | `follow23.py:96-98`: 5,000 |
| 4 | Test 3(d): AUC on the last 30% of weeks | `follow23.py:182`: last 30% of rows |
| 5 | Covariates: run length, abs(premium), hour-of-day or weekend | `follow23.py:181`: adds a flx/km dummy, no hour-of-day |
| 6 | Spread = live half-spread x 3, 1 bp floor | `follow23.py:107, 163`: a missing half-spread defaults to 5 bp |

Questions: who checks the code against the locked rule before it runs, and why did no one here? This is the third PK arbs test round in two days with a design problem (register row 7). What is common to the three?
