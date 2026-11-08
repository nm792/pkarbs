# CS2: would a faster feed fix the zero fills? And is there a faster public feed? (4 Nov 2026)

Thread "Find a faster CS2 live feed". Data: live capture in this container, 09:00-12:25Z 4 Nov (updated 12:45Z; first version 10:45Z) (raw in
`raw/2026-11-04/`, copy in `/mnt/project-files/cs2-feeds/2026-11-04/`), plus the pilot dry run
(`live/cs2_pilot/runs/2026-11-04-dry/`).

## Method
- `capture.py`: Polymarket sports WS (CS2 scores, local receive time) + full order book for every Match / Map 1-3
  Winner token of live CS2 games, polled every 1 s via `POST /books` (the CLOB market WS host is not on our network
  allowlist) + bo3.gg current matches every 3 s (mirrors Thunderpick live odds).
- `pull_trades.py`: data-api v2 trades for those markets.
- `analyze.py`: for each within-map round change on the sports WS (time R), take the rising token (>= 1c move from the
  median mid 45-90 s before to 30 s after). Market reaction time Tm = start of the largest 3 s mid step in
  [R-75 s, R+5 s]. Then:
  - fast price P_fast = pre-event mid x 0.975 floored to the tick (what the coded rule bids if it sees the event at
    Tm); size resting at P_fast 30 s and 2 s before Tm.
  - slow price P_slow = mid at R x 0.975 (what the pilot bids); size at P_slow 30 s before Tm and at R.
  - prints on that token at or below the price in the 30 s after we would join.
- Sample (12:45Z): IEM Beijing tier 1 = MongolZ-FURIA and NaVi-Falcons, full matches, 146 event x market rows;
  smaller events (CCT qualifiers, United21) 70 rows. Liquid-BetBoom had no WS round updates while recorded.

## 1. Was the queue there before the event? (medians)

| | IEM Beijing (146 rows, 2 matches) | smaller events (70 rows) |
|---|---|---|
| size at P_fast 30 s before market move | 2,753 sh | 113 sh |
| size at P_fast 2 s before market move | 2,238 sh (IQR 230-3,787) | 117 sh |
| size at P_slow 30 s before market move | 0 sh | 0 sh |
| size at P_slow when our slow bot joins (R) | 3,301 sh | 147 sh |
| our price vs best bid at R | 2 ticks below | 2 ticks below |
| size at best bid 2 s before move | 1,639 sh | 64 sh |

- At the price the slow bot uses, the queue formed AFTER the market moved (empty 30 s before, ~3,300 when we arrive):
  other bots re-stack 2.5% under the new mid faster than our WS tells us.
- At the price a fast bot would use (2.5% under the pre-event mid), a median ~2,200-2,800 shares were ALREADY resting
  before the move in tier 1. 68% of the size at P_fast 2 s before the move was already there 30 s before.
  So in most windows a faster feed swaps a post-event queue for a pre-existing one of similar size.

## 2. Would a fast bot have been filled anyway?
First version (10:45Z, 35 rows) said ~0. The full day changes that, so treat fills as UNRESOLVED:
- Prints at or below P_fast in the 30 s after the move, minus the size resting ahead 2 s before: fills in 30 of 146
  tier-1 windows, 43,700 shares total (~$15k cost). But 53% comes from ONE window (NaVi-Falcons map 1, 10:34Z,
  23,000 shares) and 87% from four. All four have zero size resting at P_fast and an event time 58-72 s before
  the WS update, so the "event" may be a different price move than the round.
- Slow bot (P_slow at R, after the queue ahead): fills in 2 of 146 windows, 11,700 shares. The pilot's own log: 0 naive
  paper fills on 18 orders.
- Markout: 1-min mid after those fast fills is +11% on cost, but that is biased upward, because rows are picked as the
  token that went on to rise. It is not a P&L estimate.
Bottom line: speed does not get us ahead of the standing queue in most windows. A minority of windows (about 1 in 5)
saw the queue cleared and prints through the fast price. Sizing that needs true round/kill times (HLTV scorebot
thread, server run 6 Nov) rather than times read off the price.

## 3. Round-score feeds are late by construction
In tier 1 the Polymarket mid makes its largest step a median ~32 s before the sports WS round update (IQR 21-55 s,
146 rows; smaller events 41 s). The pilot's half-move measure gave ~16.5 s. Either way the market is pricing kills and the bomb
DURING the round. A round-end feed, even one with zero delay, arrives after most of the move. To get ahead you need
kill-level data (GRID official feed, HLTV scorebot), not a faster round score.

## 4. Sources checked (from this container, honest UA, no bot-wall bypass)

| source | result |
|---|---|
| Polymarket sports WS | reference; round scores only, ~16-55 s behind the price |
| bo3.gg API (allowlisted) | no live rounds; Thunderpick odds mirror refreshes about every 72 s (median, n=29). Too slow |
| Cito (paid, already tested) | ~186 s behind PM |
| HLTV scorebot (scorebot-lb.hltv.org) | Cloudflare challenge (cf-mitigated: challenge) |
| Sofascore esports | 403 from Sofascore |
| PandaScore | needs paid token for live |
| Pinnacle / Thunderpick / Smarkets odds, Liquipedia, Steam/GOTV relay, Twitch, FACEIT, ESL, ScoreGG, 5eplay, Strafe, theScore | not on our network allowlist (proxy refuses), not measured |
| GRID Open Access | free application for fans/independent devs; covers in-game CS2 data for IEM/ESL circuits; terms look non-commercial. Nick asked GRID for pricing, no reply |

No public source faster than ~16 s was reachable. The only kill-level sources are GRID (paid/licensed) and HLTV
scorebot (Cloudflare).

## Confidence
- Queue pre-exists at the fast price: 7/10 (146 rows, 2 tier-1 matches, one day).
- Fills for a fast bot: 4/10, unresolved (concentrated in 4 windows with doubtful event times).
- No faster public source reachable: 8/10 (cross.bet not on the allowlist, untested; HLTV scorebot being tested from
  the server by thread "Time HLTV live scoreboard on CS2", agent/tasks/hltv-scorebot.md).
- Event time is estimated from the price (largest 3 s step), not a true round-end clock, so the WS-lag number is a
  range (16-55 s), not a point.
- Books are 1 s polls from the cloud container, so size can be off by a second's worth of changes.
