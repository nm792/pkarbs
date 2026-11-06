# Server-member heartbeat (pkarbs / project-thread-vg2ckg)
Round: 2026-11-06 13:16 UTC
- thesports-trial RUNNING healthy (books 412k, mqtt_connect rc Success). Reviewer released the 'try #' trial (12:08Z); env edit + capture restart STEP-4 gated -> waiting on Nick. Revert: restore empty THESPORTS_TOPICS line.
- nba-books-ws: Part B scheduled via `at` job 5 at 23:25Z 6 Nov (books.jsonl + out-2026-11-07); cs2 logger running (restarted ~09:57Z). 30-min copy job to winmodels/raw/nbacap-2026-11-07 armed once capture live; 00:15Z pass check.
- oddspapi multi/hist/tennis, cricket feeds, cs2/dota/hltv/lol per approved windows; inbox files have outbox replies on tip.
Waiting on Nick: thesports THESPORTS_TOPICS env edit + capture restart (#4/#164). cs2 restart not re-raised (prior approved stop; no new go).
