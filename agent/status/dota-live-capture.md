# status dota-live-capture (4 Nov 2026)

**State:** STARTED 2026-11-04T05:46Z. Capture running (node, pid 4050172; timeout 47000s; MemoryMax 400M scope).
**Window:** capture 2026-11-04T09:45Z .. 22:45Z (wait was skipped, capture active since 09:45Z).
**Last heartbeat:** 2026-11-04T13:10Z UTC
**Valve reachability:** REACHABLE from this box. GetLiveGames/v001 returned a live game set (200 OK). Confirmed.
**Output:** /root/dotacap/out-2026-11-04/ — books/realtime/league_games/rt_polls/opendota_live/sportsws + capture.log all writing (13:08Z mtimes).
**Repo copy refreshed this round (13:10Z):** all six jsonl + capture.log → `winmodels/raw/dotacap-2026-11-04/*.gz`, committed (this was the first copy — nothing had been copied before).
**Errors:** none. (One `books.jsonl: file size changed while zipping` is expected for a live-growing file; gzip produced a valid point-in-time snapshot.)
**Next checks:** copy every 30 min → winmodels/raw/dotacap-2026-11-04/; cleanup + confirm process gone at end (22:45Z+).
**waiting for Nick:** none — read-only capture, runs directly.
