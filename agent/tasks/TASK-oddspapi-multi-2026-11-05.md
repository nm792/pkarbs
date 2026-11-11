# TASK: OddsPapi historical odds for past matches of other sports (NBA, NHL, NFL, cricket, rugby, LoL, CS2, Dota)

From: Claude in the PK arbs thread "Find feeds serious sports bettors use", 5 Nov 2026 04:55Z. Requested by Nick at 04:49Z: "Can we not try the odds feed on past matches of other sports?" Status: OPEN.

## Question (one only)
Download Pinnacle, bet365 and 1xbet timestamped price history for finished matches from 16 Oct to 5 Nov 2026 in 8 sports. The thread then tests whether those books move before the Polymarket price, using PM trades it pulls itself.

## Pass / fail, fixed before running
- PASS: log.jsonl ends with `"ev": "done"`, `hist_ok` >= 100, and `hist/` has files for at least 5 of the 8 sport prefixes (nba_, nhl_, nfl_, cricket_, rugby_, lol_, cs2_, dota_).
- FAIL: anything else. Report the last 20 lines of log.jsonl. Retry at most once.
- No orders and no P&L. Read-only HTTPS to api.oddspapi.io only.

## Key
Use the installed OddsPapi key: env `ODDSPAPI_KEY` or `~/.oddspapi_key`. The script strips the key from the account log line. Never write the key to the repo, logs or outbox.

## Cost and load
`/v4/historical-odds` is free. Billable calls: 1 account, 1 bookmakers, and 24 fixtures (8 sports x 3 one-week windows). The script stops if the account shows fewer than 60 requests left. At most 480 hist calls, one every 5.3 s, so about 45 min. It runs as a single process with a 300 MB memory cap. Expected output is a few tens of MB gzipped. The tennis book logger uses different hosts.

## Run
```
cd <repo> && git pull
python3 live/oddspapi/test_pull_hist_multi.py        # must print "5 of 5 checks pass"
mkdir -p /root/oddspapi/multi-2026-11-05
systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 timeout 3900 \
  python3 live/oddspapi/pull_hist_multi.py /root/oddspapi/multi-2026-11-05
```

## Report
1. `tar czf oddspapi_multi_2026-11-05.tar.gz -C /root/oddspapi multi-2026-11-05` and commit it to `rn1/scores/oddspapi/multi-2026-11-05/` on the default branch.
2. Write `agent/status/oddspapi-multi.md` with the start and end times, hist_ok per sport, PASS/FAIL, and `df -h /` after it ends. Clean up by deleting /root/oddspapi/multi-2026-11-05 after the commit.
3. Reply in `agent/outbox/2026-11-05-oddspapi-multi.md`.
