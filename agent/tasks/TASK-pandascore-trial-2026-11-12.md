# TASK: PandaScore Low Latency trial capture, Dota 2 + CS2 (BUILD NOW, KEY COMES LATER)

Deadline: capture code tested and ready by 16 November 2026. Nick emailed PandaScore on 12 November 04:15Z asking for WebSocket access to BOTH Dota 2 and CS2 for 17 to 30 November. The key will arrive by email; Nick puts it in /etc/pkarbs/pandascore.env (PANDASCORE_TOKEN=...) himself. Do not ask him to relay anything. Starts automatically when the file exists. If the capture stalls or is not ready by 15 November 18:00Z, raise an IT issue immediately; do not wait overnight.

Locked plan and test: feeds/NOTE-pandascore-trial-plan-2026-11-10.md (project files), section 4. Use the pass bar below, which supersedes the +5 s bar there. Do not change rules after data.

## Part A: capture (chrony-synced clocks, data on /vol2 only)
1. Build a PandaScore live WebSocket client (live.pandascore.co; docs: developers.pandascore.co, low-latency-feed-overview). One connection per live match, max 3 connections unless PandaScore says more (the reply is awaited; read agent/inbox for it). Prioritise matches by Polymarket volume, high first.
2. Log per message: local receive time (ns), the raw payload, `updated_at`, and a sha1. Never discard raw messages. Log reconnects, gaps, out-of-order `updated_at`.
3. In parallel record Polymarket CLOB books (1 s) and trades plus the PM sports WS for the matched CS2 and Dota 2 markets (existing recorders), Record TheSports (live/thesports/capture.py) for the same matches as a side comparison only.
4. Dry-run the client on any public/sandbox endpoint available before the key arrives; report in outbox/status what was tested.

## Part B: analysis (locked)
- Event = state change diffed from consecutive messages. CS2: round score change (primary), `alive` count change (secondary, only if populated). Dota 2: increase in kills, towers, barracks or roshans.
- Match to PM market by team names plus start time; side by settlement, never by price co-movement.
- Lead = time of first PM mid move of >=2c in the event direction inside [-60 s, +60 s] around our receipt time, minus receipt time. Positive = PandaScore first. Always show real next to the random-time placebo (10 random event-free times in the same match) with n.
- PASS per game: the benchmark is the POLYMARKET PRICE, not TheSports. n >= 30 events, median (real minus placebo) lead >= +2.0 s, bootstrap 95% CI (resampled by match) excludes 0, and the price moves AFTER the PandaScore message in >= 60% of events. Strata: PM match volume < $25k and >= $25k, reported separately.
- TheSports comparison is information only (it was 10-60 s behind the PM price on CS2); not a pass condition.
- Money bar (only if PASS): paper rule from the plan, EUR 400/day per title.
- Else: no lead, drop that title.

## Deadlines
- Code ready: 16 November. First capture the minute the key arrives (expected 17 November).
- Verdict: 1 December (trial ends 30 November). Written feedback to PandaScore is part of the deal: Nick sends it; prepare a one-page summary.
- Status in outbox/status every 30 minutes while blocked; first status by 06:00Z 12 November.
