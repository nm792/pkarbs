# TASK: LoL event-only pilot on Worlds QF DK vs BLG (5 Nov 22:00Z), then T1 vs KC (6 Nov 22:00Z)

Code: `live/lol_pilot/` (README there). Built on `live/cs2_pilot/` (same venv, same key file).

**Mode:** DRY unless `agent/inbox/2026-11-05-lol-pilot-live-ok.md` exists and says Nick approved live. If it does,
write `/root/lolpilot/out/LIVE_OK` (content: the inbox file name + time) before starting, and run `--mode live`.

**Question:** does the pilot see LoL kill events on time on the server, place bids by the rule, and (live) get filled?

**Pass/fail, fixed before the run** (`python3 ../cs2_pilot/report.py /root/lolpilot/out/pilot.jsonl`):
1. geoblock recorded, `blocked: false`  2. >= 20 kill events  3. >= 10 windows opened
4. no bid at/above best ask or above mid x 0.975  5. feed delay measured on >= 10 events  6. no error with where=main
Live only, extra: preflight row `live_ready` present (if `halt` instead, report the reason verbatim and fall back to dry).

**Run (PROTOCOL rules 1-6):**
```bash
cd <repo>/live/lol_pilot && python3 test_lol_pilot.py      # must end "24 of 24 tests pass" (replay part skips if files absent: then 22 of 22)
mkdir -p /root/lolpilot/out
systemd-run --scope -p MemoryMax=512M -p MemorySwapMax=0 timeout 28800 \
  /root/cs2pilot/venv/bin/python lol_pilot.py --mode dry --out /root/lolpilot/out --hours 8 \
  >> /root/lolpilot/out/stdout.log 2>&1 &
```
- Start at **21:30Z 5 Nov** (match 22:00Z; the bot needs >= 30 s of book history before the first kill). 8 h cap.
  Repeat for 6 Nov 21:30Z (T1-KC) with the same out folder (state.json keeps the loss limit across runs).
- Hourly while running: copy (not append) pilot.jsonl gzipped + summary.json to `live/lol_pilot/runs/<date>/`, commit,
  write `agent/status/lol-pilot.md` with report.py output.
- Stop early: `touch /root/lolpilot/out/STOP`. Clean up: confirm exit, report `ps` and `free -m`, keep the out folder.
