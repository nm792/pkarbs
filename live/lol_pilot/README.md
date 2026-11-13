# LoL event-only live pilot (capped), Worlds 2026

Plan item "LoL event-only live test before the Worlds final (14 Nov)". Built on the CS2 pilot (`../cs2_pilot`, PRs #51/#53):
same order handling, caps, kill file, heartbeat, paper fills, markouts and report. Only the trigger and model differ.

| file | what |
|---|---|
| `lol_pilot.py` | the bot (dry or live); docstring has the rule and caps |
| `test_lol_pilot.py` | offline tests + replay of GEN-LYON game 1 (4 Nov); must print "24 of 24 tests pass" |
| `../cs2_pilot/report.py` | summary + gates (its "round events" = kill events here) |
| `../../agent/tasks/lol-pilot.md` | server task for Hermes |

## Rule as coded (= `rn1/scores/lol/bidsim/kills_only.py`)
- Trigger: kill-count change on the Polymarket sports WS (`homeKills-awayKills|games|BoN`), net kill change for home dk != 0.
- Jump: P(home wins game) = sigmoid(logit(base) + 0.284 x dk) - base; base = book mid 30 s before the WS update
  (WS shows kills ~12.5 s after the price moves, so base must predate it).
- If |jump| >= 1c and the mid has not moved by the jump: for 30 s rest a post-only BUY at token mid x 0.975 (rounded UP to
  1c, never below market - 2.5%), only on the rising side, only if fair - bid >= 1c, never at/above the best ask. Hold to resolution.
- Markets: `Game k Winner` of the game in play, Worlds/MSI events only. Not traded: Match Winner, handicaps, props.

## Caps
5 shares per order, $5 per match, $20 total loss limit (halts at -$20 realized). The CS2 pilot's own $40 limit uses the
same $50 account. Live needs the trade-only session key (`/etc/pkarbs/pm-session.env`), geoblock pass and `OUT/LIVE_OK`.

## Backtest expectation (simulated, not measured)
`out_kills_only.txt`, holdout 531 games, 500-share cap: WS-like lag (2 + U(0,20) s) +$10.7k to result, 90% [+0.7k, +20.5k];
at 20 s lag +$6.3k [-3.0k, +15.5k]. The live test exists to measure what the sim cannot: real queue and fills at our price.
