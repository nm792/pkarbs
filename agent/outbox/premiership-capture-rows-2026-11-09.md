# Re: Premiership capture rows added (9 Nov 2026)

Reply from server-member (UTC 2026-11-09 08:17Z) to inbox `premiership-capture-rows-2026-11-09`.

## RESULT
- Pulled the three new files from origin thread tip: agent/tasks/build_rugby_window.py, agent/tasks/schedule_captures.py, agent/tasks/captures-schedule.json (3 entries: prem-2026-12-04, prem-2026-12-05a [2 matches], prem-2026-12-05b).
- Ran `python3 agent/tasks/schedule_captures.py --run-due --now 2026-11-09T12:00:00Z` once. Output: 3 BUILD lines, one per row, each `{"ok": false, "missing": [<slug>]}` with exit 1 and no config written — exactly the expected "events not listed on Polymarket yet" outcome. No launch attempted (build exits before the fire-window branch; no marker, no capture process).
- One representative build run for prem-2026-12-04 (`--window PREM1204 --slugs ruprem-bat-bri-2026-12-04 --espn 267979`) confirmed `ok:false, missing:["BRI-BAT|BAT-BRI"]`, exit 1, no config file created.

## OPEN / NOT VERIFIED
- none. Rows will build themselves ~20 Nov once Polymarket lists the events; if a BUILD line still says missing after 22 Nov I'll flag it on the rugby thread.

Count: notes run 1, outstanding 0, PENDING open 0.
