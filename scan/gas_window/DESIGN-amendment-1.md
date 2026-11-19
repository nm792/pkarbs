# Amendment 1 to DESIGN-nowcast-backtest-v1.md (19 Nov 2026 ~05:35Z, before any forward data)

Reason: Nick, 19 Nov 05:27 to 05:29Z: the v0 model already lost to the favourite on the 28 development days, so it is not the candidate; the daily jump is taken to be the AAA data release at about 03:15 ET (settled by Nick; consistent with the Polymarket sweep at 03:14 to 03:36 ET on 24 of 28 days).

1. Candidate slot is EMPTY. nowcast.py (blob 4001a87f) is renamed in the text to BASELINE-v0: it is scored forward at no cost for reference only, never as the pre-registered candidate.
2. Entry time: just before the release, fixed at 03:05 ET on D (primary). The bar is the market favourite at 03:05 ET on the same events, about 86% on the development days (without 14 Nov 85%). The v1 pass rule (section 7) is unchanged: at least +5 pp with a paired day-bootstrap 95% lower bound above 0 on n of 30 forward events, otherwise FAIL.
3. Candidate v2 inputs must be knowable before 03:05 ET: state-level AAA prints (jgreathouse9/AAAGas MasterGas.csv, internal research use, no licence file found), intraday gasoline futures, station-level crowd prices. v2 will be fixed in a separate committed file (formula, parameters, fitting) after a state-versus-national lead test on days BEFORE 22 Oct, and not before. If no candidate beats 86% there, the finding is FAIL for the nowcast route.
4. The alternative route is not a forecast: reading the AAA page at the flip faster than the existing sweeper. It is tested only after aaa_watch.py has timestamped the flip (it/REPLY-2026-11-19-0535Z). Fills against the real book come from pm_gas_books.py (blob f14392db), recorded 02:50 to 03:45 ET.
5. Development sample, 14 Nov handling, fees and fill rules: unchanged from v1.
