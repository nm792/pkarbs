# Chess sizing for in-play trading (8 Nov 2026)

Data: gamma series 11480 (Polymarket "chess" league, resolves on lichess.org), all 121 resolved per-game events; every data-api v2 trade per market (raw in raw/, split in chess_events_split.json, script pull_split.py). Notional = size x price. In-play = market gameStartTime to +7 h (or closedTime). Each game has 3 markets (white win / draw / black win).

| Event | Games | Pre-match $ | In-play $ | In-play at 5-95c $ | In-play $/game | Best game in-play |
|---|---|---|---|---|---|---|
| FIDE Candidates 2026 Open (31 Mar-15 Apr) | 48 | 106,495 | 95,311 | 26,313 | 1,986 | 9,414 |
| FIDE Candidates 2026 Women | 40 | 4,344 | 23,506 | 690 | 588 | 5,821 |
| Grand Chess Tour Poland rapid/blitz (6-9 May) | 33 | 942 | 9,418 | 119 | 285 | 2,111 |
| Total | 121 | 111,781 | 128,234 | 27,122 | 1,060 | |

Findings
- Per-game chess markets exist only for 3 events, all Mar-May 2026. Nothing per-game in the last ~6 months (Aug-Nov: only Titled Tuesday and Olympiad/Candidates-Qualifier outrights). No open per-game market today.
- Total in-play notional across ALL 121 games = $128k, about $27k in the 5-95c band where a bid can matter. That is under $2k/day averaged over the 3 months and about $10k on the busiest Candidates days. Not a $100/day sport on current evidence; the best case (Candidates Open) is roughly $2k in-play per game.
- Next real event: FIDE World Championship, Gukesh vs Sindarov, Geneva, game 1 on 24 Nov, 14 classical games to 11 Dec, tiebreaks 12 Dec (dates vary slightly by source). Outright market "2026 World Chess Championship: Winner" already $173k gamma volume. Whether Polymarket lists per-game markets for it, and how big, is UNKNOWN. Settled by: markets appearing around 22-24 Nov.

Live feed options (all untested for lag)
- Lichess broadcast API (lichess.org/api/broadcast/...) streams moves and clocks of official events (reachable from this environment after the allowlist change, 8 Nov). Lichess is also Polymarket's resolution source. Engine eval is computed by us (Stockfish) or taken from Lichess cloud eval.
- Official FIDE/DGT board relays are the upstream of those broadcasts.
- chess.com api.chess.com: allowlisted, not examined.

Does the Polymarket price lag engine-eval swings? UNKNOWN. No open per-game market and no move timestamps for the Candidates games exist in our data, so no placebo-controlled lag can be stated. Settled by: a capture of the PM book plus the Lichess broadcast move stream (with our own eval) for a World Championship game, compared to random-time placebo.

Plain reading: even an instant feed is volume-limited here. Chess games also move on slow, large eval swings (blunders), so the event-only rule would fire a handful of times per game.

Confidence 7/10 on the volume table (complete for the series; gamma tag search may miss a per-game event outside series 11480; in-play window assumption of 7 h). Confidence 2/10 on any profit or lag statement (none made).
