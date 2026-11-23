# IT TASK (deploy only, paper backtest on Prime per R-039): R-036 item 1 final rerun with data to 23 Nov, due 12:00Z 23 Nov

From the pipeline thread. Read-only data pulls and one-shot scripts; no orders, no keys. Do not edit code. Nick does not SSH; you run and paste. Input data: `/mnt/project-files/pipeline/R036/pk_cache_min.tgz` (49 MB, sha256 starts 0f91df9934af237d: 18,694 events of the 81 families + 15,458 trade tapes to 19 Nov).

1. `cd /mnt/HC_Volume_107257520/pkarbs && git fetch origin claude/project-thread-o5rbz8 && git checkout FETCH_HEAD -- pipeline it`; paste commit id and `sha256sum pipeline/late_leader.py pipeline/late_pull.py pipeline/refresh_events.py`.
2. `python3 -m pytest -q pipeline/tests/test_late_leader.py pipeline/tests/test_resolving_books.py` (expect `16 passed`; run from the repo root).
3. Data off the root disk: `mkdir -p /mnt/HC_Volume_107257520/pk_cache && tar xzf /mnt/project-files/pipeline/R036/pk_cache_min.tgz -C /mnt/HC_Volume_107257520/pk_cache && ln -sfn /mnt/HC_Volume_107257520/pk_cache /home/user/pk_cache` (the scripts hard-code /home/user/pk_cache; a symlink only).
4. REPRODUCTION (must match before anything else counts): `cd pipeline && python3 late_leader.py > /mnt/HC_Volume_107257520/pk_cache/ll_repro.log 2>&1 && python3 -c "import pandas as pd; d=pd.read_csv('out/listing1/late_leader_families.csv'); print(round(d.L1_pnl_day.sum(),2), round(d.hs_pnl_day.sum(),1), len(d))"`. Expected `53.07 867.7 81`. Any other number: STOP and paste both outputs.
5. FINAL: `python3 refresh_events.py ../it/resolving_books_series.txt && python3 late_pull.py && python3 late_leader.py` (about 15 min; refresh adds the 19-23 Nov events, late_pull fetches their tapes at 10 threads, about 2,000 markets). Paste the same one-line print as step 4 and `cp out/listing1/late_leader_families.csv /mnt/project-files/pipeline/R036/late-leader-families-final-2026-11-23.csv`.
6. Health read (R-037) in INBOX: command exit codes, `wc -l ll_repro.log`, number of `Traceback` lines (expect 0), disk free, and that prices are own-token trade prints (field: tape column 3 `price` of the traded `token_id`, never 1 minus the other side).

The pipeline thread then writes the final table from the CSV. Without this run the final stays the 22 Nov numbers (FLOOR, tapes to 19 Nov).
