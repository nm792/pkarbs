# status: thesports-trial (TASK-thesports-trial-2026-11-05)

- **REAL TOPICS WIRED + LIVE (2026-11-06T15:50Z).** 5 issued topics in `THESPORTS_TOPICS` (basketball/tennis/lol/dota2/csgo `.match.v1`), plus `THESPORTS_POLL_PATHS=/v1/lol/match/detail_live@2`. Chunk `final-topics-24925` running, `mqtt_connect rc=Success`, all 5 subacks `Granted QoS 0`.
- **4/5 topics DELIVERING:** 107 msgs first minutes — basketball 32, csgo 55, dota2 18, tennis 2. Full event payloads (CS2 kills + per-player stats, Dota2 pick/ban, basketball quarters + timer).
- **LoL = 0 msgs, HTTP `/v1/lol/match/detail_live` → "URL is not authorized to access, please contact our business staff."** LoL not yet authorized on account (task: LoL first priority, Worlds semis 7–8 Nov). Thread must ask TheSports to authorize LoL.
- Capture healthy: books/markets/pmws growing, Polymarket recording running. Same read-only rules.
- Prior results: `#` refused (suback "Unspecified error", reverted). Real topics now supersede it.
- Values never printed. Backups: env `/root/thesports.env.bak-pretopics` + `/root/thesports.env.bak-pre-topic`.

- **CORRECTION (22:18Z): the LIVE writer is chunk `final-topics-8917`**, not 24925. `ps` shows capture.py writing /root/thesports/final-topics-8917 started 15:48Z; fresh books.jsonl 946 MB @21:18Z. Chunk 24925's files stop 15:50Z (its commit of suback+discover_pm is the 15:50 snapshot, since pushed). Both chunk dirs were wired with the same real topics; the running capture is healthy and writing. LoL still 0 msgs / HTTP "URL not authorized".
