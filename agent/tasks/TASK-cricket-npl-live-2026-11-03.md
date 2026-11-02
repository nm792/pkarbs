# TASK: Nepal PL live ball-by-ball capture, 3 Nov 2026 (ESPN feed lag vs Polymarket)

From: Claude in the PK arbs thread "Build per-sport win-probability and EV rules" (2 Nov 2026). Requested by Nick. Status: OPEN.

## Question (one only)
For each ball in two Nepal PL T20 matches, when does the ESPN ball-by-ball feed show it, compared with when the Polymarket match-winner price moves? We measure the signed lag from our receive time to the nearest 2c trade move, for wickets and boundaries.

## Pass / fail, fixed before running
- PASS for a match: the logger runs from start minus 15 min to the result; at least 90% of 5 s polls return data; and there is no gap over 60 s with no successful poll while the match is in play.
- FAIL: either condition is not met. Report which, and give no lag figures for that match.
- No P&L.

## Code (repo, merged)
`evrules/live_pbp_logger.py`. It runs one process, polls `site.api.espn.com` every 5 s, writes jsonl, copies it to `--share` every 10 min, and stops itself after `--minutes`.

## Windows (one process each, never overlapping)
| | ESPN (cricinfo) id | Match | Start (ESPN) | Run |
|---|---|---|---|---|
| A | 1558593 | Biratnagar Kings v Janakpur Bolts | 3 Nov 06:45Z | 06:30Z, 255 min |
| B | 1558594 | Lumbini Lions v Pokhara Avengers | 3 Nov 10:45Z (PM says 11:15Z) | 10:30Z, 255 min |

Window B starts 15 min before window A's run ends. Kill window A first, as soon as A shows the result, and confirm it has stopped. If A is still running at 10:30Z, stop it and note that in the report.

```
cd <repo> && git pull
systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 timeout 15600 \
  python3 -m evrules.live_pbp_logger cricket 1558593 --minutes 255 --every 5 \
  --out /root/cricket-live --share /root/cricket-live/share
```
(Window B: id 1558594.)

## Polymarket (for the analysis after each match; no polling needed during play)
- A: conditionId `0x8789ba37b5065400132541a1c329d0ffb76e4a26b7377931cc6499cc7566ae50` (outcomes: Biratnagar Kings, Janakpur Bolts)
- B: conditionId `0xbdd9f1db3fc483ffad9b71e1ad04568bcc81073ea802e7cb07cbe6b660885f7e` (outcomes: Lumbini Lions, Pokhara Avengers)
- After each match, pull every trade with `GET https://data-api.polymarket.com/trades?market=<conditionId>&limit=500&offset=<n>` and save it next to the jsonl as `trades_<id>.json`.

## Report
1. Commit the jsonl and trades files to `rn1/scores/cricket/live-2026-11-03/` on a branch.
2. Write `agent/status/cricket-npl-live.md` with: start and stop times, the pass/fail result per window, polls, empty polls, rows, and the output of `ps` and `free -m` after each window (cleanup).
3. Reply in `agent/outbox/2026-11-03-cricket-npl-live.md`. The thread does the lag analysis itself.

## Protocol notes
- This is a light poller, one curl every 5 s. It runs alongside the always-on WS logger and the LoL capture (LoL windows are at 22:00Z, so they do not overlap).
- Use an honest User-Agent. Do not work around any 403.
