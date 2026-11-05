# TASK: OddsPapi historical odds pull for 4-5 Nov (Pinnacle / bet365 vs Polymarket price)

From: Claude in the PK arbs thread "Find feeds serious sports bettors use" (5 Nov 2026, 02:05Z). Requested by Nick (he set up the OddsPapi free key with Hermes, 02:01Z). Status: OPEN.

## Question (one only)
Download OddsPapi's timestamped Pinnacle, bet365 (plus one more live book) price history for every finished or live tennis, CS2, LoL and Dota fixture between 2026-11-04T00:00Z and 2026-11-05T12:00Z. The thread then tests whether those books move BEFORE the Polymarket price on matches we already captured.

## Pass / fail, fixed before running
- PASS: log.jsonl ends with `"ev": "done"` and `hist_ok` >= 20, and `hist/` holds at least one CS2 or LoL fixture and at least 10 tennis fixtures.
- FAIL: anything else. Report the last 20 lines of log.jsonl. Do not retry more than once.
- No orders and no P&L. Read-only HTTPS to api.oddspapi.io only.

## Key
Use the OddsPapi key Hermes already installed: env `ODDSPAPI_KEY`, or the file `~/.oddspapi_key`. Never write the key to the repo, logs or outbox.

## Cost and load
`/v4/historical-odds` is free and never counts against the quota. The billable calls are about 6 in total: 1 sports, 1 bookmakers, and 1 fixtures call per sport. The script keeps to the API cooldowns (5.3 s between hist calls), so it makes one request every ~5 s. It runs for at most ~40 min, as a single process with no overlap; the running cricket-feeds logger uses different hosts.

## Run
```
cd <repo> && git pull
mkdir -p /root/oddspapi/2026-11-04
systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 timeout 3600 \
  python3 live/oddspapi/pull_hist.py /root/oddspapi/2026-11-04
```
Offline test (no network): `python3 live/oddspapi/test_pull_hist.py` must print `4 of 4 checks pass`.

## Report
1. `tar czf oddspapi_2026-11-04.tar.gz -C /root/oddspapi 2026-11-04` and commit it to `rn1/scores/oddspapi/2026-11-04/` on the default branch (expected size a few MB).
2. Write `agent/status/oddspapi-hist.md` with the start/end times, hist_ok, PASS/FAIL, and `ps` / `free -m` output after it ends (cleanup: delete /root/oddspapi after the commit).
3. Reply in `agent/outbox/2026-11-05-oddspapi-hist.md`. The thread does the analysis.
