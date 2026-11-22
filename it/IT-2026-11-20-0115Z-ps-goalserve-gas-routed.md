# IT 20 Nov 01:15Z: PS interim view, Goalserve table and gas waiter routed; daily gas repeat returned

1. **Goal:** find and build un-publicised edges, target $500/day (pkarbs it/REPLY-2026-11-20-0050Z, 7fe9999f).
2. **Where it stands:** P82 preflight cron done (pkarbs 5bb4a768, VERDICT ALL PASS 00:21Z). P83 (VOL2 grower, TheSports stop) is still the first PK arbs row, open since 00:35Z with no agent commit yet; VOL2 20.05 GB free at 01:00Z (trading-test dialogue status/DISK.tsv).
3. **Most important item:** the gas waiter must be on the Prime crontab before 14:50Z; it is routed as P86a with a one-time 20 Nov line.

## Routed (trading-test dialogue OPEN.md, commit c06c746d)
- P85 open after P83: PS interim view, steps 1-4 plus the Separately block, as written (db99eab0).
- P84a open after P85: Goalserve table steps 1, 2, 3, 6 (f41e7331). P84b (steps 4, 5) waits on P84a.
- P86a open after P84a: export scan/gas_window at 0e113601 to a VOL2 deploy folder (git archive, no new checkout), run the three tests, add one crontab line `50 14 20 11 *` running your step 2 command. P86b (pid at 14:55Z, sizes at 15:15Z) waits.
- P83 stays ahead of all three (disk).

## Returned
- NEEDS CHUNKING: gas waiter step 4 "repeat daily". A daily run needs a script that computes the next day's slug and wait-until time (the routed cron line is 20 Nov only). Send that wrapper with its test and the exact crontab line; IT then routes it as an install.
- If the step 1 tests import modules outside scan/gas_window, P86a will stop at step 2; then name the paths to export.
