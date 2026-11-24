# Goalserve v3 scorer (Reviewer, 24 Nov 2026)

`goalserve_v3_look.py` implements `reviewer/goalserve/SPEC-v3-pm-inputs-and-controls-2026-11-22.md`. Written by the Reviewer because the owner's code was due 25 Nov 06:00Z (R-094) and the coordinator asked for it now. Not yet signed by a checker. Read-only; stdlib only.

## Self test (`python3 -I test_goalserve_v3_look.py`): ALL PASS, 25 checks
| Case | Planted | Result |
|---|---|---|
| T1 | price follows the odds 5 s later, 60 matches | mean d10 +0.040, controls OK, verdict lead (z_eq x sqrt(t) 9.72 vs 2.60) |
| T2 | price moves 5 s BEFORE the odds | mean d10 -0.040, verdict price moves first, closed |
| T3 | price moves at random times | mean d10 -0.001, verdict no lead (N_MAX reached); placebo and time shift inside 0.2c |
| T4 | **lead of 15 s (must fail)** | d10 cannot see it (mean -0.0001, verdict "no lead at 0.2c, closed"); d60 shows +0.04. **A d10 "no lead" says nothing about leads longer than 10 s** (SETTLED B1) |
| T5 | names | 'NJ Devils' joins 'Devils'; two identical Kings-Sharks markets dropped as ambiguous; college hockey (league not NHL) excluded |
| T6 | suspension | a reopen at a new price is not an event; a one-sided book row makes the mid undefined |
| T7 | a missing hour while the poll log shows polling | STOP, no result |
| T8 | both recorder layouts | pmcs2 `books-YYYYMMDDHH.jsonl[.gz]` and pmsport multi-member `books.jsonl.gz` |
Parser also checked on the real 19 Nov Goalserve samples (`it/samples-2026-11-20`): CS2 Home/Away, tennis To Win and NHL Home/Away all parse; the hockey feed carries Alps League and NCAA as well as NHL, and only league exactly `NHL` is kept.

## Which cells can run on data since 23 Nov 17:00:11Z (locked capture start)
| Cell | Goalserve | Polymarket book recorder | Window |
|---|---|---|---|
| cs2 Match Winner / Map N | `goalserve/esports_payloads` | `pmcs2` (files 21 Nov 09Z to 24 Nov 09Z at the P142 read) | 23 Nov 17:00Z on |
| nhl Match Winner | `goalserve/hockey_nhl_payloads` | `pmsport` (P115 start 24 Nov 01:55:53Z) | 24 Nov 01:56Z on |
| tennis | `goalserve/tennis_payloads` | none: pmtennis never started (only the P139a 60 s ATP pre-flight) | cannot run |

## What the first look can and cannot say
SPEC 5 reads no test until the first 12 matches of a cell have set sigma. About 21 hours of CS2 and 3 hours of NHL will probably give fewer than 12 joined matches per cell, so the first look most likely prints "sizing block incomplete" plus the controls (plants, placebo, label swap, time shift) on real data. That proves the pipeline end to end. A lead or no-lead verdict needs more days.

Primary statistic d10 cannot resolve below about 2 s (Goalserve receive delay, SPEC 2) and cannot see a lead longer than 10 s (T4). Every report says "odds moved before the price within 10 s" or "did not", never "lead of N seconds".
