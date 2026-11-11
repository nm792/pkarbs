# TASK: Tennis 1 s Polymarket order books + OddsPapi latency probe, 5 Nov 2026

From: Claude in the PK arbs thread "Find feeds serious sports bettors use" (5 Nov, 04:10Z). This is the requested follow-up to Nick's "why 5-10 s and not 2?" (PR #112). Status: OPEN.

## Question (one only)
Record 1 s Polymarket order books (top 15 levels) for every live tennis moneyline, until 20+ tennis matches have been covered in play. The thread then re-runs the Pinnacle-triggered tennis backtest with real queue position. It also logs (a) the CLOB round-trip time from the server and (b) how fresh OddsPapi's Pinnacle/bet365 odds are when we receive them.

## Pass / fail, fixed before running
- PASS: books.jsonl grows through the run, markets.jsonl lists 20 or more distinct tennis events with start times inside the run, and probe.jsonl has 10 or more `clob_rtt` rows.
- FAIL: the process dies early, or books.jsonl stops growing for more than 10 min while markets are live. Report the last 20 lines of log.jsonl.
- No orders and no P&L. Read-only: POST clob /books (about 1 per second per 50 tokens), gamma every 5 min, GET clob /time every 60 s, and at most 120 billable OddsPapi calls (capped at 30% of the remaining free quota; `/v4/account` is unmetered). The script never logs the API key.

## Code
`live/tennis_books/capture.py` (copied from the cricket logger; standard library only, no websockets).
```
cd <repo> && git pull
mkdir -p /root/tennis-books/2026-11-05
systemd-run --scope -p MemoryMax=500M -p MemorySwapMax=0 timeout 43500 \
  python3 live/tennis_books/capture.py /root/tennis-books/2026-11-05 12 \
  --share /root/tennis-books/2026-11-05/share
```
The OddsPapi key comes from env `ODDSPAPI_KEY` or `~/.oddspapi_key`, as in the OddsPapi task. Start as soon as you read this. Expected size is about 50 MB/hour of raw books, about 5 MB/hour gzipped.

## Report
1. Every hour, gzip and commit `share/*.jsonl` to `rn1/scores/tennis/books-2026-11-05/` on the default branch.
2. Write `agent/status/tennis-books.md` with the start time, rows per file, distinct events, and PASS/FAIL. After it stops, include `ps` / `free -m` and delete /root/tennis-books once the final commit is in.
3. Reply in `agent/outbox/2026-11-05-tennis-books.md`. The thread does the analysis, then asks for one more free OddsPapi historical-odds pull for these matches.

## Protocol notes
This is a single light poller, like the running cricket logger, on different markets; there is no overlap. It uses an honest User-Agent (pkarbs-tennis-books) and does not work around any 403.
