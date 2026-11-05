# TASK: OddsPapi history for tennis on 5 Nov (to pair with the 1 s tennis books recorded since 05:32Z)

From the PK arbs project thread, 5 Nov 2026 08:30Z. Status: OPEN. Queue it AFTER TASK-oddspapi-multi2 (both are small and free).

## Question
Download Pinnacle, bet365 and 1xbet price history for every finished tennis fixture from 2026-11-05T00:00Z to the time you run it (they pair with the 1 s Polymarket books the recorder has been saving). The existing pull stopped at 02:46Z, so 5 Nov matches after that are missing. The thread then re-runs the tennis Pinnacle-trigger backtest with queue position from the real books.

## Pass / fail, fixed before running
- PASS: log.jsonl ends with `"ev": "done"` and at least 30 tennis files in hist/.
- FAIL: anything else; report the last 20 log lines. Retry at most once. Read-only; free hist endpoint; about 2 billable calls.

## Run (disk gate: root >= 6 GB free, hard stop < 5 GB)
```
cd <repo> && git pull
mkdir -p /root/oddspapi/tennis-nov5
systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 timeout 3300 \
  python3 live/oddspapi/pull_hist.py /root/oddspapi/tennis-nov5 2026-11-05T00:00:00Z <NOW-as-ISO-Z> --max-fixtures 250
```
(The script keeps tennis plus CS2/LoL/Dota fixtures in the window; esports are pulled first and are fine to keep.) Tar to `rn1/scores/oddspapi/tennis-nov5-2026-11-05/` (each file under 100 MB) on the default branch, delete /root/oddspapi/tennis-nov5, status in agent/status/oddspapi-tennis-nov5.md, reply in agent/outbox/2026-11-05-oddspapi-tennis-nov5.md. Never commit the key.
