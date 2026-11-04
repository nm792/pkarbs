# CS2: would a faster feed fix the zero fills? And is there a faster public feed? (4 Nov 2026)

Thread "Find a faster CS2 live feed". Data: live capture in this container, 09:00-10:45Z 4 Nov (raw in
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
- Sample: 54 round events, 78 event x market rows. IEM Beijing tier 1 = MongolZ-FURIA (35 rows); other = ILLYRIANS-Bebop
  CCT qualifier (43 rows). NaVi-Falcons, Liquid-BetBoom had too few WS round updates while recorded.

## 1. Was the queue there before the event? (medians)

| | IEM Beijing (35 rows) | CCT qualifier (43 rows) |
|---|---|---|
| size at P_fast 30 s before market move | 3,734 sh | 230 sh |
| size at P_fast 2 s before market move | 2,657 sh | 200 sh |
| size at P_slow 30 s before market move | 0 sh | 0 sh |
| size at P_slow when our slow bot joins (R) | 3,942 sh | 251 sh |
| our price vs best bid at R | 2 ticks below | 2 ticks below |
| size at best bid 2 s before move | 1,530 sh | 51 sh |

- At the price the slow bot uses, the queue formed AFTER the market moved (empty 30 s before, ~3,900 when we arrive):
  other bots re-stack 2.5% under the new mid faster than our WS tells us.
- At the price a fast bot would use (2.5% under the pre-event mid), ~2,700-3,700 shares were ALREADY resting
  before the move in tier 1. So a faster feed swaps a post-event queue for a pre-existing one of the same size.
  57% of the size at P_fast 2 s before the move was already there 30 s before.

## 2. Would a fast bot have been filled anyway?
Prints at or below P_fast in the 30 s after the move (IEM rows): 6 of 35 windows had any; total 6,215 shares against
126,569 shares resting ahead of us at P_fast 2 s before the move. Last in line, fills are ~0. Even first in line
it is ~180 shares per window. The pilot's own log agrees: 0 naive (first-in-line) paper fills on 18 orders.

**Answer: no, speed alone does not fix the zero fills.** At the rule's price (mid - 2.5%) the size is already
resting before the event, and few prints reach that price after it.

## 3. Round-score feeds are late by construction
In tier 1 the Polymarket mid makes its largest step a median ~44 s before the sports WS round update (IQR 25-61 s;
CCT 36 s). The pilot's half-move measure gave ~16.5 s. Either way the market is pricing kills and the bomb
DURING the round. A round-end feed, even one with zero delay, arrives after most of the move. To get ahead you need
kill-level data (GRID official feed, HLTV scorebot), not a faster round score.

## 4. Sources checked (from this container, honest UA, no bot-wall bypass)

| source | result |
|---|---|
| Polymarket sports WS | reference; round scores only, ~16-44 s behind the price |
| bo3.gg API (allowlisted) | no live rounds; Thunderpick odds mirror refreshes about every 72 s (median, n=29). Too slow |
| Cito (paid, already tested) | ~186 s behind PM |
| HLTV scorebot (scorebot-lb.hltv.org) | Cloudflare challenge (cf-mitigated: challenge) |
| Sofascore esports | 403 from Sofascore |
| PandaScore | needs paid token for live |
| Pinnacle / Thunderpick / Smarkets odds, Liquipedia, Steam/GOTV relay, Twitch, FACEIT, ESL, ScoreGG, 5eplay, Strafe, theScore | not on our network allowlist (proxy refuses), not measured |
| GRID Open Access | free application for fans/independent devs; covers in-game CS2 data for IEM/ESL circuits; terms look non-commercial. Nick asked GRID for pricing, no reply |

No public source faster than ~16 s was reachable. The only kill-level sources are GRID (paid/licensed) and HLTV
scorebot (Cloudflare).

## Confidence: 6/10
- Queue result: 2 tier-1 maps in one match (35 rows) plus one small match. More IEM Beijing matches (5-8 Nov) would
  lift it to 8/10; the capture keeps running.
- Event time is estimated from the price (largest 3 s step), not a true round-end clock, so the WS-lag number is a
  range (16-44 s), not a point.
- Books are 1 s polls from the cloud container, so size can be off by a second's worth of changes.
