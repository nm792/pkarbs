# agent/outbox/thesports-cricket-lol-mqtt-2026-11-09.md

Status: QUEUED - not yet executed. Nick's 12:14Z 9 Nov note pre-approves ("routine step, no further approval needed"), but the terminal consent gate blocks a cron from (a) writing the edited THESPORTS_TOPICS to the pkarbs thesports env file and (b) restarting the live capture (thesports-capture-b scope, pid 2818605). Both need the on-box tap; a headless cron cannot clear it.

PLAN (ready to run on the tap)
1. Backup the env file -> /root/backups/thesports.env.pre-cricket-20261109.
2. Set THESPORTS_TOPICS to six topics: thesports/basketball/match/v1, thesports/tennis/match/v1, thesports/cricket/match/v1, thesports/lol/match/v1, thesports/dota2/match/v1, thesports/csgo/match/v1. NOTE: LoL (thesports/lol/match/v1) is ALREADY present in the current env; only cricket is the addition.
3. Restart capture once via start_writer.sh (thesports-capture-b), verify capture pid alive, RSS under cap.
4. Report restart time, mqtt_suback for each of the six topics, message counts per topic after 10 min and after 1 h. Suback errors / zero-message topics quoted verbatim for Nick -> TheSports.

Revert: restore the pre-cricket backup of the env file and restart the capture once (removes cricket, back to 5 topics).
