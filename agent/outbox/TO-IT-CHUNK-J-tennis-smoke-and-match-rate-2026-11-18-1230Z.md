# P27 — Goalserve tennis smoke and name-match counts (18 Nov 2026)

- Clean export source: pkarbs commit `09b9665e64f56daf0095048828073f6fede87517` (the required chunk-J code is present). Exported `feeds/` to scratch; no checkout pull, stash, or cleanup.
- Smoke exit 0 at 13:06:44Z; no traceback/error in the required log tail. `sport=tennis`, `smoke_not_a_result=True`, two input files, 1,575 events.
- Audit: rows 3,752; `skip_bad_odds=2674`; `skip_suspended=4845`; `To Win=94405`; league prefix `tennis=95671`; drops: no PM market 541, match cap 262, tie d zero 15, one-sided PM book rows 4,333, PM book timestamps from milliseconds 126,296.
- 43 matches with events: PM candidates 0/1/2+ = **13/30/0**. The smoke is diagnostic only; no cells or verdicts are reported.
- Evidence: Prime data-volume scratch `pkarbs/scratch/goalserve-tennis-smoke-20261118/smoke.json` and `smoke.log`; 06/07 input checksums match the earlier chunk-I copies.
- No capture, configuration, process, or live code was changed.

OPEN / NOT VERIFIED
- None for this smoke item; this is not a result or a tennis-trial verdict.
