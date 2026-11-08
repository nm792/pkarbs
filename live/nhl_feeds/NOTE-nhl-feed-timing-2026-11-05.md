# NHL: feed lag against the Polymarket price, and the event-only rule's delay curve (5 Nov 2026)

Thread "Time NHL feed against the price". Strategy as always: bid market minus 2.5% after a goal, only on the side the model says should rise and has not yet, below the ask, held to resolution (not market making).

## 1. How late is each feed vs the Polymarket price (measured live, 4 NHL games on 4-5 Nov, 14 goals with a >=2c price move)
Price onset = first 1 s book snapshot with >=20% of the goal's move (moves are one step: half-move = onset).
| source | median after onset | range | goals under 30 s |
|---|---|---|---|
| ESPN's own goal timestamp (wallclock) | -1.3 s (ESPN stamps the true event time) | -2 to 0 | n/a (not receivable that early) |
| NHL api-web (cache-busted 1 s poll), score change | **50 s** | 8 to 70 s | 5 of 14 |
| ESPN summary API (2 s poll) | 64 s | 20 to 90 s | 3 of 14 |
| Polymarket sports WS | 95 s (it sends NHL once a minute) | 52 to 123 s | 0 of 14 |
Earlier nights (3-4 Nov, 85 goals, server frames): WS median 78 s after onset (p10 41, p90 131). Script ws_lag_past.py.
- By the time the NHL feed arrives the price has moved a median 87% (1.0 = fully).
- Racing api-web endpoints (play-by-play, landing, boxscore, score-by-date, each cache-busted at 1 s) on 5 goals: all within 1 s of each other. No faster NHL endpoint exists. The default (uncached-busted) URL is cached up to 19 s, so a plain poll is worse still.
- Depth at our bid (mid -2.5%) when the NHL feed arrives: median ~320 shares, 4 of 14 goals had none.
- One goal dropped (same score reached twice, a reviewed goal), 8 goals had under 2c price move or no book.

## 2. Event-only rule at true event time plus a delay (past games, 640 games, 2025-26 and Oct-Nov 2026)
True event time = price onset. Settings fixed on Oct-Dec 2025 (177 games): bid for 60 s, min model jump 4c. First in queue assumed (optimistic). 500-share cap, $ per game held to resolution (90% range of the total in brackets, 235 test games):
| delay | Jan-Apr 2026 (test) | Oct-Nov 2026 (228 games) |
|---|---|---|
| 0 s | $19.9 ($2.4k to $7.2k) | $5.2 |
| 5 s | $17.4 | $3.6 |
| 20 s | $17.7 | $4.6 |
| 30 s | $12.9 | $4.3 |
| 60 s | $3.5 (spans zero) | $2.7 |
Volume-limited, not speed-limited inside 30 s. NHL runs ~4-11 games a night (~7 average), so ~$140/day at <=20 s on the test half but only ~$35/day on this season so far (sim).

## 3. Verdict
- Polymarket's score stream: useless for NHL (95 s late).
- Free NHL feed (api-web): median 50 s late -> worth about $3-13/game (about $20-90/day, sim), the low end on this season.
- Only a feed under ~30 s pays, and then only $13-20/game in last season's test half versus ~$5 this season, so NHL is a ~$35-140/day candidate even with a perfect feed. Official NHL data is Sportradar (10-year deal); price unknown, almost certainly not worth it for this size. Not pursued.

## Files
live/nhl_feeds/ (capture.py, live_lag.py, endpoint_race.py, ws_lag_past.py, out_*.json), winmodels/us/ (s1_hist_nhl.py, nhl_delay_hist.py, out_nhl_delay_hist_*.json). Raw: /mnt/project-files/nhl-feeds/2026-11-05/run1-3, winmodels/raw/us_nhl_hist (+ tar in /mnt/project-files/winmodels/raw/).
Confidence 7/10: the 0-30 s result is firm in sign but optimistic in size (first in queue); 14 live goals is a small live sample, but all four sources agree with the 85-goal past-night check.
