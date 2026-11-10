# Cricket gate: NOT yet applied — gate reply corrected

Status: DONE-AS-FAR-AS-CRON-CAN; the previously-filed "already live" gate reply was WRONG and is corrected here.

CORRECTION (measured 2026-11-10 00:3xZ): the cricket topic is NOT live, and no restart has loaded it.
- /etc/pkarbs/thesports.env THESPORTS_TOPICS holds FIVE topics only (basketball/tennis/lol/dota2/csgo). No cricket line.
- Running capture `thesports-capture-b.scope` (pid 2818605) started 2026-11-08 00:39Z — BEFORE Nick's 12:14Z 9 Nov approval — and its loaded env carries those same five topics.
- Zero `thesports/cricket/match/v1` rows have ever been captured (topic was never in the env).

## What the approval covers
Nick's 12:14Z 9 Nov note pre-approves the step ("routine, no further approval needed"): add `thesports/cricket/match/v1` to THESPORTS_TOPICS, restart the capture once, report suback + per-topic counts after 10 min. The reviewer note also says "do it yourself, or give a one-tap card."

## The precise blocker (the one thing this needs)
The edit targets the system config file `/etc/pkarbs/thesports.env`. In this unattended cron context the terminal consent gate BLOCKS the write (copy/move into system config path) with no user present to clear it. This is the ONLY gate — the approval itself already exists.

Ready-to-run on an on-box clear (one command each, ungated prep is done — backup exists):
1. `/root/bin/start_writer.sh` restart with the edited env; or
2. interactive: `cp -a /etc/pkarbs/thesports.env /root/backups/thesports.env.pre-cricket-20261110 && sed -i 's#thesports/tennis/match/v1#thesports/tennis/match/v1,thesports/cricket/match/v1#' /etc/pkarbs/thesports.env` then restart thesports-capture-b with the same systemd-run args.

Revert: restore /root/backups/thesports.env.pre-cricket-20261110 and restart once.

NOT a one-tap approval card to Nick — Nick already approved this on 9 Nov. It needs an ON-BOX console clear only.
