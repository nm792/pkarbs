# HLTV scorebot (kill-by-kill) timing vs Polymarket, 4 Nov 2026

Thread "Time HLTV live scoreboard on CS2". Measured on real data, 1 capture, 3 matches. Confidence 8/10 on the verdict.

## Verdict
HLTV's live scoreboard is about **2 to 3.5 minutes behind** Polymarket's own sports score stream, and that stream is
already behind the Polymarket price (round updates arrive ~16-44 s after the price moves, PR #63 / pilot dry run).
So HLTV kills arrive roughly **2.5-4 minutes after the price has moved**. HLTV scorebot is useless as a fast CS2 feed.
The cause is almost certainly the tournament broadcast (GOTV) delay that the scorebot inherits; our connection's
reconnects cannot explain minutes (offsets are steady round after round).

## How it was captured
- `agent/tasks/hltv-scorebot/capture.js` (PR #73) ran on Nick's MacBook 12:50-16:00Z (Hermes never picked up the task).
  HLTV match pages returned Cloudflare challenges (403, `cf-mitigated: challenge`) and were not bypassed; the public
  scorebot socket (scorebot-lb.hltv.org, socket.io v2, listId = HLTV match id) accepted the home connection and sent
  kills, but dropped and reconnected every ~5 s (≈2,200 disconnects per match), replaying recent history each time.
- Polymarket books 1 s (POST /books, 11,350 polls, 0 errors). Mac clock vs Polymarket book timestamps: median +0.24 s.
- Raw: `live/cs2_feeds/raw/hltv-2026-11-04/` (scorebot.jsonl.gz 31.6 MB, books, markets, http, capture.log).

## Measurements (computed on the raw data)
1. **HLTV round score minus Polymarket sports WS round score**, MEIA NOITE vs Damajuana (CCT South America), 21 rounds over
   two maps (`hltv_rounds.py`, WS frames from the server cs2-ws-logger copy of 17:17Z):
   median **+137 s**, quartiles +127 / +151 s, minimum +120 s. HLTV was later on every round.
2. **NAVI vs Falcons map 3 (IEM Beijing)**, by eye from the same two files: 12-0 at WS 12:48:31 vs HLTV 12:51:33 (+182 s);
   12-3 at WS 12:58:18 vs HLTV 13:01:38 (+200 s); map end at WS 12:59:59 vs HLTV 13:03:33 (+214 s).
   (WS for this match refreshed every ~20 s, so ±10 s.)
3. The kill-vs-price event study (`hltv_lag.py`) has only 16 usable kills (MEIA NOITE map markets, the only open map
   markets captured; ~$2k traded; NAVI's price was outside 3-97c). It shows the price already moving before every kill
   that moved it (8 of 8), but the ±60 s window is far shorter than the true ~2.5 min lag, so its -26 s median is not a
   delay estimate. Measurement 1 is the delay figure.
4. The MongolZ vs FURIA connection only replayed a finished map (no live data).

## Queue
Irrelevant now: even a zero-delay feed would sit behind the ~3,700 shares already resting at mid-2.5% before the event
(PR #63). A feed that is minutes late cannot help.

## Next
- Run 2 (IEM playoffs, 6 Nov) cancelled: same broadcast delay.
- Kill-level CS2 data fast enough to beat the price only comes from in-server sources (GRID, official data partners),
  which are out (GRID paid: corporate only). CS2 fast-feed search is closed unless a new source appears.
