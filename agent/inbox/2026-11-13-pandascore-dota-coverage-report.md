# To Hermes, 13 Nov 15:50Z: PandaScore Dota coverage report, due in agent/status/pandascore.md by 16:15Z

Asked by Nick's coordinator via the TheSports thread ("can we check Dota with another feed"). The locked Part B in TASK-pandascore-trial-2026-11-12.md v2 (STANDARD v1) already covers Dota; no second test. This is a count, not a test. Do not change any rule.

Please add to agent/status/pandascore.md by 16:15Z:
1. Of the Dota 2 sockets open since 15:12Z (4 at start), how many are on matches that have a Polymarket Game-N-Winner (or match-winner) market, matched by team names plus start time. The TheSports side has had no new PM-paired Dota game since 11 Nov, so this is the bottleneck.
2. Dota 2 state changes captured so far (kills, towers, barracks, roshans diffed per `game_id`) with Polymarket price coverage (rows from the PM recorder within +/-60 s). Count events and distinct matches. Label "sim on real data" only if analysed; otherwise just counts.
3. Estimated dates to reach 30 priced Dota events and about 10 distinct matches with PM price coverage (needed for a match-clustered CI), from the live schedule (`/matches?filter[low_latency_feed]=true`) and PM listings, naming BLAST Slam from 17 Nov. LABEL IT AN ESTIMATE and state the assumptions.

No verdict and no lead claim: counts and an estimate only.
