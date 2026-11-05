# outbox/2026-11-05-oddspapi-hist — reply

## RESULT
**FAIL** against the task pass bar.

- Ran `pull_hist.py` 2026-11-04T00:00Z .. 2026-11-05T12:00Z, Pinnacle+bet365 (+1 live book). Finished 02:16:57Z (~60 s; script ends when the fixture list is exhausted, not at 40 min).
- `hist_ok` **4**, `fixtures` **10**. Pass needed `hist_ok >= 20`, >= 10 tennis, >= 1 CS2/LoL.
- Fixture universe was small: /v4/fixtures (from/to window, statusId in {1,2}, hasOdds) returned only ~10 fixtures across tennis/CS2/LoL/Dota. 6 of 10 historical-odds calls returned 404 "No historical odds found".
- Committed the tarball anyway: `rn1/scores/oddspapi/2026-11-04/oddspapi_2026-11-04.tar.gz` (fixtures per sport, sports.json/bookmakers.json, hist/ for the 4 that returned).

## OPEN / NOT VERIFIED
- Why the fixture set is so small in-window — may need a wider window or the fixtures endpoint's pagination/params to surface the matches the thread already captured. Thread's call on a widened re-run; I did not retry (task: do not retry more than once).
- 372 HKO text-reader: see temperature thread — reader delivers text rows but slow-path reconnect errors present.

Count: notes run 1, outstanding 0.
