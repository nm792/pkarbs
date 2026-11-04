# TASK: Cito tennis WebSocket logger (always-on style logger, bounded per day)

Owner thread: "Run Cito setup and time feeds" (branch claude/project-thread-7f1y2j). Written 4 Nov 2026. Requested by the
tennis thread for its point-level backtest.

**Status: WAITING FOR KEY.** Do not start until `/etc/pkarbs/cito.env` exists. Nick sends the key to Hermes in his direct chat;
Hermes installs it per `live/cito_timing/KEY-INSTALL-CITO.md`. Never print, copy, commit or message the key.

## Question (one only)
Does the Cito tennis WebSocket (room "all") deliver every POINT_UPDATE for live ATP/WTA/Challenger/ITF matches over a
full day, with our receive time on each line, next to the Polymarket sports WS tennis rows?

## Pass / fail, fixed before running
- PASS: over the first 12 h, the logger is connected at least 95 percent of the time (gaps = time between a `*_err` line
  and the next `*_open`), and at least 20 distinct Cito match_ids have 50 or more POINT_UPDATE lines each.
- FAIL otherwise. Report the gaps and error lines. No P&L, no delay figures in this task (the tennis thread computes them).

## Run (PROTOCOL rule 2: one process, memory cap, time limit)
```bash
pip install --user websocket-client   # if missing
cd <repo checkout> && set -a && . /etc/pkarbs/cito.env && set +a && \
systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 timeout 43200 \
  python3 -I live/cito_timing/tennis_logger.py 43000 /root/cito_tennis/out /root/cito_tennis/copy
```
- On a server without /root/.ccr/ca-bundle.crt the script uses the system CA store automatically.
- Hourly UTC files `cito_tennis_YYYYMMDDTHH.jsonl`; gz copies refreshed every 30 min in `/root/cito_tennis/copy`.
- Raw volume ~26 MB/hour uncompressed (~2-3 MB gz) while many matches are live.

## Copy out
Every hour, commit the gz files from `/root/cito_tennis/copy` to the repo under `data/cito-tennis/` on branch
`hermes/cito-tennis` (not the default branch), then check the committed files contain no `cito_` key string
(`zgrep -l 'cito_[A-Za-z0-9_-]\{25,\}'` must print nothing; the logger redacts it, this is a second check).

## Clean up (rule 4)
At the 12 h limit the process exits. Confirm with `ps` and `free -m`, delete `/root/cito_tennis/out` after the final
copy is committed, and write `agent/status/cito-tennis-logger.md` with connected-time percent, match count, and the pass/fail.
