# TASK: OddsPapi history for cricket and rugby in the window Polymarket actually listed (small follow-up)

From the PK arbs project thread, 5 Nov 2026 ~07:15Z. Status: OPEN. Reason: the first multi pull took the most recent cricket and rugby fixtures (1-4 Nov and 23 Oct-1 Nov), but Polymarket only has cricket moneylines up to 29 Oct and rugby (Premiership/URC) up to about 10 Oct plus a few on 23 Oct, so none matched. This pull targets the overlap.

## Question
Download Pinnacle, bet365 and 1xbet price history for finished cricket fixtures 8 Oct to 30 Oct and rugby fixtures 8 Oct to 25 Oct.

## Pass / fail, fixed before running
- PASS: log.jsonl ends with `"ev": "done"` and `hist_ok` >= 30, with both `cricket_` and `rugby_` files in hist/.
- FAIL: anything else. Report the last 20 log lines. Retry at most once. Read-only; free hist endpoint; about 8 billable fixtures calls; stop if the account shows < 60 requests left (the script checks).

## Run (disk gate as ruled: root >= 6 GB free; hard stop < 5 GB)
```
cd <repo> && git pull
python3 live/oddspapi/test_pull_hist_multi.py     # 5 of 5 checks pass
mkdir -p /root/oddspapi/multi2-2026-11-05
systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 timeout 2400 \
  python3 live/oddspapi/pull_hist_multi.py /root/oddspapi/multi2-2026-11-05 \
  --from 2026-10-08T00:00:00Z --to 2026-10-31T00:00:00Z --sports cricket,rugby --cap 120 --total 240 --oldest
```
Tar per sport (each under 100 MB) into `rn1/scores/oddspapi/multi2-2026-11-05/` on the default branch, delete /root/oddspapi/multi2-2026-11-05, status in agent/status/oddspapi-multi2.md, reply in agent/outbox/2026-11-05-oddspapi-multi2.md. Never commit the key.
