# Alternative in-play score sources — 2026-10-30

Task `agent/TASK-sports-alt-sources-2026-10-30.md` (queued until TASK-tennis-cs2-coverage DONE + report; coverage report now committed → this ran next). Honest UA `pkarbs-research/1.0 (contact nm@delphic.co)`, robots-first, one process per run, ≥5 s pacing.

## Request log (URL | status | bytes)
| ts UTC | URL | status | bytes |
|---|---|---|---|
| 03:44 | https://site.api.espn.com/robots.txt | 403 | 387 |
| 03:44 | https://cdn.nba.com/robots.txt | 000 | 0 |
| 03:45 | https://api.pandascore.co/robots.txt | 403 | 28 (`{"error":"Token is missing"}`) |
| 03:46 | https://api.pandascore.co/csgo/matches (1 unauthenticated req per "needs a key" clause) | 403 | 28 (`{"error":"Token is missing"}`) |
| 03:47 | https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json | 000 | 0 |

Total 5 requests (budget 20). ★ note: ESPN robots = 403 → per hard rule (403 = stop, no alternate route), the ESPN scoreboard/summary paths were **not** fetched. The PandaScore unauthenticated API call is the single one the task's key-clause permits to record the auth failure, then stop.

## One row per host
| host | robots | API/page status | play-by-play present? | why not |
|---|---|---|---|---|
| site.api.espn.com | 403 (Access Denied) | not attempted | **no — stopped per hard rule** | robots.txt itself is 403 at the edge (Akamai); hard rule: record 403, stop on host, don't try another route. NBA scoreboard/summary (play-by-play source) therefore not reachable under these rules. |
| cdn.nba.com | 000 (no connection, retry also 000) | 000 | no | host unreachable from this box (both robots and the public scoreboard JSON returned 000/no connection — DNS/routing, not an HTTP deny). The live play-by-play JSON that exists on this CDN is not reachable here. |
| api.pandascore.co | 403 (`Token is missing`) | 403 (`Token is missing`) | no | API requires a token; only the single unauthenticated request recorded (403). No key requested — task forbids it. CS2 playback route blocked. |

## PASS / FAIL (fixed before the run)
- **NBA pass rule: FAIL.** Neither NBA host (site.api.espn.com, cdn.nba.com) returned play-by-play with clock times + running scores for a 22–29 Oct game. ESPN is robots-403 (stopped on host by the hard rule); cdn.nba.com is unreachable (000). No plays recorded.
- **PandaScore row:** recorded — 403 (token). A result, not a task failure.

## Overall verdict (which source to use next)
- NBA play-by-play **is** publicly available on `cdn.nba.com`'s JSON endpoint in general, but it is **not reachable from this server** (000 on both robots and the scoreboard JSON). ESPN's API is blocked at the edge (robots 403). 
- **Recommendation:** for NBA play-by-play with running scores, a browser-session source (e.g. ESPN's JS-rendered scoreboard via the browser, or a permitted scores site) is the next candidate — but under this task's hard rules (honest curl, no workaround for a 403) no reachable option exists to test further here. For CS2, no key-free, robots-allow, non-SPA source was found (HLTV disallowed, bo3.gg SPA, PandaScore keyed). Flag for the reviewer: in-play scores for rn1's CS2/NBA markets need either a browser-driven fetch permit (outside this task's curl-only rule) or an allowed API key.

## Cleanup
- `shadow/alt-sources-raw/` empty (ephemeral bodies in /tmp, removed). No processes remain.
- `ps` own procs: none (logger pid 2951556 is unrelated).
- `free -m`:
```
               total        used        free      shared  buff/cache   available
Mem:            7746        3578         365           4        4114        4167
```

No IPs, host names, volume names or keys.