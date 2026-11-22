# Audit: PK arbs (gas daily paper run) against MODELLING-PRINCIPLES.md (22 Nov 2026, 04:00Z)

Reviewer. Approved by Nick 22 Nov 03:37Z. Read-only on project code. Method: `/mnt/project-files/reviewer/MODELLING-PRINCIPLES.md` (trading-test reviewer c771fd7), sections 2-15.
Code read: branch `claude/project-thread-lfb1pf` at **9f7731e739** (`scan/gas_window/daily_rule/`): paper_post.py, paper_score.py, paper_day.py, aaa_page_log.py, aaa_page_tinyfish.py, test_paper_score.py. Accepted scoring SHA was 20293df7 (R-009); 9f7731e adds the TinyFish page logger.

## Code logic first: when is each decision made, and what is visible then

| step | file:line | what is visible | verdict |
|---|---|---|---|
| Decision time | paper_post.py:23-28, 40-44 | the first page row with status 200 showing date D; decision time = that row's `recv_ns` | depends on how recv_ns is stamped (next row) |
| **Page read time stamp** | **aaa_page_tinyfish.py:16; aaa_page_log.py:24** | `recv_ns = time.time_ns()` is taken **before** the HTTP request is sent; the response arrives later (TinyFish timeout 150 s, its own `latency_ms` is logged but not used; direct logger timeout 15 s) | **HINDSIGHT DEFECT.** The decision is placed before the page content was received, by the fetch duration. |
| Fill book | paper_post.py:43-44 | latest own-token snapshot with recv_ns in [recv_ns(page) - 3 s, recv_ns(page) + 2 s] | Because recv_ns(page) is the request-start time, the fill book can be a snapshot from before the page value reached us. The market reprices after the AAA change, so earlier books carry better asks: the bias is in the rule's favour. |
| A3 hold | paper_post.py (R-009, 20293df7) | same level and size in the first snapshot at or after read + 2.25 s, within 5 s | Clean given a correct read time; latency 2 s ASSUMED and labelled |
| Monitor route (R-019) | not yet in code | row recv_ns = "run time" | Same risk: if the monitor's run start or schedule time is used, the decision precedes receipt. |
| Settlement | paper_post.py docstring item 3 | Gamma resolution, cross-checked with page | Clean |

## Checklist

| # | item (section) | status | evidence |
|---|---|---|---|
| 1 | No hindsight: decision time and inputs (8) | **Partial (defect)** | page read stamped at request start (aaa_page_tinyfish.py:16, aaa_page_log.py:24) and used as decision time (paper_post.py:27, 43). No test asserts recv_ns >= response time (test_aaa_page_tinyfish.py:10, 17 set or ignore it). |
| 2 | Markout scoring (12) | **Done** | paper_score.py:13, 22-42: own best bid at +1 / +5 / +30 min and 10:00 ET, net of entry fee |
| 3 | Estimate, shrink, rank; delete nothing (5) | **Done (crude)** | paper_score.py:69-74 normal-normal EB over post / yes_fav / no_out; 3 cells, labelled a ranking aid |
| 4 | Multiple testing (6) | **Partial** | shrink only; 3 cells, so low priority |
| 5 | Planted edge + null + power (2, 15.4) | **Partial** | Positive control (stale ask caught up by +60 s) and null (no trade at fair ask) through paper_post/paper_score (test_paper_score.py:13-28); always-valid null-peeking test (:52). **Power is inconsistent with the registered boundary**: paper_day.py:45 `power_days(2.60, 7.06)` = 45.6 days uses the backtest SD, but the registered SD is 7.06 x 1.5 = 10.59 (paper_day.py:9), which needs 103 days. |
| 6 | Capacity per cell (14) | **Done** | paper_score.py:43-52 capacity_row at the decision moment on own-token asks that pass the rule; unfilled-hold counts reported daily (R-009). Gas already labelled capacity-limited (best $11.74/day vs $200). |
| 7 | Sequential success/futility stops, max sample (13) | **Done, but cannot reach success at the backtest edge** | paper_score.py:53-68: normal-mixture CS (Howard et al. 2021), registered sigma, success LB > 0, futility UB < 0, max 60 days then "inconclusive, ranked". At n = 60 and sigma 10.59 the half-width is $4.49/day, above the backtest edge $2.60/day, so SUCCESS is unreachable by design unless the live edge is ~1.7x the backtest. |
| 8 | OOS calibration vs market (9) | **Missing (shadow cells only)** | `post` uses no model (page value). yes_fav / no_out use a normal nowcast (paper_post.py:65-67, nowcast_inputs.json); no reliability or Brier vs market for it. |
| 9 | Non-stationarity (11) | **Partial** | one row per event day, unsourced days counted separately (paper_day.py:36-41). No top-5 share or drift statistic yet (too few days). |
| 10 | Forward band (7) | **Done for scope** | post counted; yes_fav / no_out shadow cells scored on frozen settings (R-015(5)). |
| 11 | Decided prices (10c) | **Done** | rule eligibility caps (rule.py) |

## Claims checked

- "PK's gas paper test has pre-fixed stop rules": TRUE (paper_score.py:61-68; SIGMA registered at paper_day.py:9). Limit: success cannot be reached within the 60-day maximum at the backtest edge, and the power figure uses the unregistered SD.

Open R-rows: OUTBOX R-020 (the read-time defect is due before 22 Nov is scored).

Confidence 8/10. To reach 9: one logged TinyFish read showing recv_ns vs response time (latency_ms) to size the offset; and the monitor-to-row converter once written.
