# Goalserve trial: dated window schedule (Goalserve thread, 19 Nov 2026 08:35Z)

Standing order (Nick 19 Nov 08:18Z): no more missed Goalserve or PandaScore windows. Trial runs to about 12 Dec (estimate; vendor email to confirm). All times UTC. Event dates for esports come from the project calendar notes (BLAST Slam IX Dota 20-29 Nov; CS2 Major 25 Nov, AT RISK); I have not verified the individual match times and the check at window start confirms live games exist (live games > 0, matched > 0) or the window is declared EMPTY, not passed.

## Rule for every window
- T-30 min: IT pastes preflight (clock, poll gap, live games, matched, books) from the capture; any failed line = fix within 15 min or name the exact blocker.
- T+15 min: plausibility read (rows growing, events > 0 or a stated reason, poll errors 0, disk > 15 GB). Implausible = kill, fix, rerun, the same window.
- T+end: result file path, commit and inputs cited; checker audit before any pass.
- Disk gate: free space is checked at T-30 and T+15; below 17 GB = P60 fallback below.

| # | window | sport / event | start | data checks | fallback (named) |
|---|---|---|---|---|---|
| W1 | now to 08:42Z | tennis + NHL/AHL hockey, probe v3 | running since 05:39Z | v3 plausibility read P59 (08:20Z), JSON 08:42Z | If the JSON is missing: read /tmp/hermes_bg_proc_c57eb8334d03.log, rerun v3 from 08:50Z for 180 min |
| W2 | daily 00:30Z-04:30Z | NHL/AHL hockey (US evening games) | 00:00Z each day from 20 Nov | T-30 preflight; Polymarket hockey books present; "Home/Away" vs moneyline OT rule stated | Tennis-only look if hockey has 0 matched games; report hockey as EMPTY that day |
| W3 | daily 08:00Z-22:00Z | tennis (ITF/Challenger/Tour) | 08:00Z each day from 19 Nov | open-market moves only; 429 window 19 Nov 03:29-05:10Z excluded | Next day's window; no sample from a day with poll gaps > 10 s over 5% |
| W4 | 19 Nov rerun | esports look 1 on 18 Nov files | after P58 | run exit 0, smoke_not_a_result false, hash cited | If the 18 Nov files are incomplete: PREREG amendment (esports start 19 Nov) for the checker |
| W5 | 20-29 Nov | Dota 2, BLAST Slam IX | each match day, T-30 | Goalserve esports live games > 0 and matched to both-token PM books | PandaScore Dota odds (PandaScore thread); declare Goalserve EMPTY if no matched games |
| W6 | 25 Nov | CS2 Major (AT RISK) | per PandaScore schedule | same as W5 | Other CS2 tier-1 events in the trial; none = EMPTY, tell Nick the same day |
| W7 | to about 12 Dec | basketball | none | NBA dropped; no capture planned | Excluded from ship_raw exception (P60) |
| W8 | 12 Dec | BBL cricket | AT RISK | No working Goalserve cricket endpoint | Ask Goalserve for the endpoint by 26 Nov; else BBL is not a Goalserve window |

## Daily rhythm
- 07:30Z: look the previous day's data (run_daily_look.sh tennis|esports) and paste the exit lines.
- 12:00Z and 18:00Z: IT pastes `df -h` and the capture last-row time.
- Every 15 min while a window is live: the reviewer-branch check (OPEN-ORDERS first).

## Known risks now
1. Disk: capture about 225 MB/hour, 0.56 GB above the floor at 08:30Z (P60).
2. Hockey odds are "Home/Away"; whether it settles on regulation or includes overtime is unverified. Stated in every hockey report.
3. Shared Goalserve key: 429 if any other process polls it. Only the capture polls.
