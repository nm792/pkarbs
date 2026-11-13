# TASK (v2, 13 Nov 2026): PandaScore Low Latency Feed capture, Dota 2 + CS2. ACCESS IS LIVE NOW, START TODAY

Benchmark and bar: feeds/STANDARD-feed-latency-test.md v1 (cite it; no deviations). Benchmark is the Polymarket price, never another feed. TheSports is information only.

## What changed (PandaScore reply 13 Nov 14:03Z)
- Low Latency Feed ACTIVATED for Dota 2 and CS2, from 13 Nov to 1 December 2026. Use the existing API token from the PandaScore dashboard: PANDASCORE_TOKEN in /etc/pkarbs/pandascore.env (mode 600). If that file does not exist yet, write one status line "token missing" in agent/status/pandascore.md and look in agent/inbox; do NOT ask Nick to relay anything, the coordinator asks him once.
- Guide (single source of truth): /mnt/project-files/feeds/PandaScore-low-latency-feed-llm-guide-2026-11-13.md (copy of their guide). Read it before coding.
- `updated_at` = the time PandaScore RECEIVES and SENDS the message (not game time). Messages can arrive out of order when a faster internal source takes over. No applied latency from their side. So lead is measured on OUR receive time only; log updated_at beside it, never use it for lead.
- Limits: 3 sockets per match per token (4029 beyond that), no limit on matches, key NOT tied to a fixed IP, 10,000 REST requests/h.
- CS2 kills and economy fields arrive "early next week" (PandaScore will say). Until then CS2 events = round score change (primary) and `alive` flips (secondary, only if `player_alive` in `available_fields`). Do not wait for them; start now.

## Part A: capture (chrony-synced clocks, data on /vol2 only)
1. Discovery: poll `GET https://api.pandascore.co/low_latency_feeds` (Bearer header, never `?token=` in logs) every 60 s. Each entry has `match.id`, `match.videogame.slug` (`cs-go` = CS2, `dota-2`), `match.opponents`, `endpoint.url`, `endpoint.opens_at`. Also `GET /matches?filter[low_latency_feed]=true` for upcoming. Keep Dota 2 and CS2 only; skip LoL.
2. Connect to `wss://live.pandascore.co/matches/{id}/low_latency_feed?token=...` at or after `opens_at` (15 minutes before start). WRONG URL is `/matches/{id}` (stream-synced). Never log a URL containing the token.
3. One socket per match. Prioritise by Polymarket match volume, high first (BLAST Slam Dota starts 17 Nov; CS2 runs daily). Optionally open a second socket per match for redundancy only if within the 3-per-match limit.
4. Read close codes: 1000 = finished, no reconnect; 1xxx or no code = reconnect with backoff (1,2,4..30 s) after closing the old socket; 4004 = re-check discovery; 4001/4003/4029 = log and stop for that match, never retry in a loop. No heartbeat exists and a silent socket is not an error; log silence duration, never kill on a timer.
5. Log per message: local receive time (ns), host, raw payload (never discard), sha1, `updated_at`, kind (hello / status / game-state), `available_fields`. Log reconnects, silent matches, out-of-order `updated_at`, close codes. After a reconnect treat state as stale until the next update (no snapshot).
6. In parallel record, against the same chrony clock, Polymarket CLOB books (1 s) plus trades plus the PM sports WS for the matching CS2 and Dota 2 markets (existing recorders; Goalserve esports and other captures may already cover some). Record TheSports for the same matches as information only.
7. Charter: this is a new collector (class 4). File whatever APPROVALS item the charter requires (as for Goalserve item 13) with exact change and revert, and tell Nick in the status file. Capture size: measure MB/day for one hour first.

## Part B: analysis (locked, per STANDARD v1; unchanged by anything in the data)
- Events: Dota 2 = increase in kills, towers, barracks or roshans (diffed per `game_id`). CS2 = round score change (primary), `alive` count change (secondary). Key state by `game_id`; match teams by team ID, not order.
- Lead, placebo, strata (PM match volume < $25k and >= $25k), pass bar: STANDARD v1 section 3. n >= 30 events per game title; fewer = "unknown, settled by <what, when>".
- Money bar only if the lead passes: STANDARD v1 section 5 (EUR 400/day per title; lower bound EUR 133/day).
- Independent audit before any pass or fail is relayed (STANDARD v1 section 4).

## Deadlines
- First capture TODAY, 13 Nov: the first CS2 or Dota 2 match with an open socket after the token exists.
- Dota 2 BLAST Slam from 17 Nov: capture must be running and verified by 16 Nov 12:00Z.
- Status in agent/status/pandascore.md every 30 minutes while blocked, and at the first live message. If not capturing by 15 Nov 18:00Z, raise an IT issue immediately.
- Trial ends 1 December. Verdict 2 December. Written feedback to PandaScore is part of the deal: prepare a one-page summary; Nick sends it.
- Do not change the rules after data.
