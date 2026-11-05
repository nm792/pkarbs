# agent/status/heartbeat.md
2026-11-05T15:10Z UTC
df -h:
- /        : 18G free / 50%
- /vol (sdb): 26G free / 45%
- /vol2(sdc): 28G free / 71%
Running now (all pkarbs, on /vol2 unless noted):
- LoL DK-BLG: ARMED (watchdog */2, inert till 20:30Z window; out /vol2/pkarbs/lol)
- cricket-feeds-v2: RUNNING (out /vol2/pkarbs/cricket/2026-11-05, ~17:47Z end)
- tennis-books-v2: RUNNING (out /vol2/pkarbs/tennis/2026-11-05, stop ~21:30Z)
- CS2/LoL/Dota/NBA: none running (paused per 381; not in restart order).
Gate: all three disk_gate GO on /vol2 (cap 20G, free 28G). Charter 383: raw to box hourly, manifest in git only.
