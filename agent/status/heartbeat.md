# Server-member heartbeat (pkarbs / project-thread-vg2ckg)
Round: 2026-11-06 13:46 UTC
- thesports-trial RUNNING healthy (capture pid up 3h13m, 12h chunk to ~22:33Z; books 610M/583k rows, pmws 4525, mqtt_connect rc Success). REVIEWER RELEASED the THESPORTS_TOPICS=# trial (12:08Z); env edit + capture restart still gated -> waiting on Nick (system-config write consents in unattended cron). Revert: restore empty THESPORTS_TOPICS line.
- nba-books-ws: Part B scheduled via `at` 23:25Z; cs2 logger + rec_ws/ff/poly all running. Copy job to winmodels/raw armed once capture live; 00:15Z pass check.
- oddspapi multi/hist/tennis, cricket feeds, cs2/dota/hltv/lol per approved windows; inbox files have outbox replies on tip.
- thesports-topics-2026-11-06.md on origin has NO same-name outbox; the reviewer's '#' instruction (12:08Z) is answered by thesports-ask-reviewer-topics + status, but a same-slug stub is warranted once the trial step actually applies.
Waiting on Nick (STEP-4, one line): approve/clear the /etc/pkarbs/thesports.env THESPORTS_TOPICS=# write + capture restart (reviewer released 12:08Z, consent-gated in unattended cron).
