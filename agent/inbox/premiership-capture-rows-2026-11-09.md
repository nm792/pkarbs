# Premiership capture rows added (9 Nov 2026) - needs one approval, see below

Nick (9 Nov 07:58Z): club rugby beyond Top 14 must be covered, Premiership first. Premiership, URC and Champions Cup are all off until the autumn internationals end: Premiership resumes Fri 4 Dec 19:45Z (BAT-BRI) and Sat 5 Dec (GLO-NEW 15:00Z, HAR-LEI 15:05Z, SAR-NOR 17:30Z).

New in this commit (all on vg2ckg, stdlib only):
- agent/tasks/build_rugby_window.py: builds a capture window from Polymarket event slugs; exits 1 and changes nothing if the events are not listed yet (Polymarket lists ~2 weeks ahead, so expect ~20 Nov).
- agent/tasks/schedule_captures.py: rows may carry slugs+espn; --run-due builds the window first, then launches at kickoff minus 15 min (no launch attempt until the build works).
- agent/tasks/captures-schedule.json: 3 rows (prem-2026-12-04, prem-2026-12-05a with two matches, prem-2026-12-05b).
- agent/tasks/rugby-top14-capture.py: ESPN league per window (Premiership 267979); run length = last kickoff + 2h35 for these windows. Windows A, AB, C, D behave exactly as before (diff is 9 lines, only active when a window event has espnLeague).

Hermes, next round: pull; run `python3 agent/tasks/schedule_captures.py --run-due --now 2026-11-09T12:00:00Z` once (expect three BUILD lines with ok:false, no launch); reply in agent/outbox/premiership-capture-rows-2026-11-09.md. No further action until ~20 Nov, when --run-due builds the windows by itself; if a BUILD line still says missing after 22 Nov, tell the rugby thread.

## Update 08:50Z (Nick: also URC and Champions Cup)
Added 4 rows: urc-2026-12-04 (2 matches, 19:45Z), urc-2026-12-05 (6 matches, 12:30Z-19:45Z), cc-2026-12-11 (2 matches, 20:00Z), cc-2026-12-12 (7 matches, 13:00Z-17:30Z). These rows use `prefix`+`dates`: build_rugby_window.py discovers every Polymarket event whose slug starts with ruurc-/rueuchamp- and ends with that date, so team codes are not needed. Same behaviour: build fails cleanly until listed. The URC 5 Dec window runs about 10 h (12:15Z to ~22:20Z); the rest 3-7 h. Expected load: up to 6 matches x 3 markets x 2 tokens per window, same as Top 14 AB.
Test: discovery built T (ruurc 2026-10-31) and T2 (rueuchamp 2026-10-18) from past events OK.
