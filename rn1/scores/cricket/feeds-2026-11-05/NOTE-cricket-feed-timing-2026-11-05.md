# Cricket feed timing vs the Polymarket price, 5 Nov 2026 (interim, data to 09:01Z)

Question: for BBL (12 Dec), do the free cricket feeds show wickets and boundaries before the Polymarket price moves? Rule under test: after an event, bid mid minus 2.5% (post-only, below the ask) on the side the model says should rise 1c or more and has not yet; hold to resolution. Not market making.

## Feeds
- ESPN ball-by-ball (site.api.espn.com playbyplay, polled every 1 s): works, ~0.1 s per poll. Used.
- ESPNcricinfo: Akamai 403 from our IP. Not usable.
- Polymarket sports WS: now sends cricket frames, but only a running score string per match (no wicket or boundary event). Not analysed yet.

## Result 1: ESPN is about 30 s behind the price (measured, 92 events, 3 matches)
Event-triggered average of the batting team's mid, signed (wicket down, boundary up), time k relative to when our poll first saw the ball (live/cricket_feeds/eta.py):
- total move by +90 s: 3.8c. Already done by the time ESPN shows the ball: 87% (3.3c).
- half the move (1.9c) has happened by k = -30 s. The move starts around -45 s.
- placebo (random times, random sign): flat, within 0.13c.
- by play: all three types (four, six, out) show the same shape; see eta.json by_play.
So there is only ~0.5c of the move left when ESPN reports it, against a bid 2.5% under mid. The rule on the ESPN feed has no room.

## Retraction
The first interim read in the thread (median 15 s, "price first on 77%") used a first-1c-move-in-a-window detector. A placebo (random times) gave the same or larger numbers (median 19-32 s), so that number was an artefact. Do not use it. The event-triggered average above is the valid measurement.

## Result 2: delay curve, NOT conclusive
analyze.py simulates the rule at T0 + 0/5/10/20/30/60 s, with T0 = ESPN receipt (anchor 0) or ESPN minus 30 s (anchor 30, = a feed at true event time). Fills come from real trades at or under our bid, minus queue ahead at our price. Only ONE match is resolved (Strikers v Heat, Heat won by 14), and each delay has 0-5 fills, so P&L swings of ±$200 are noise. No verdict from this curve yet. Thin markets: Strikers v Heat 623 trades / $52k; Thunder v Scorchers 196 trades / $36k so far; NPL 139 trades / $1.7k.

## Next
- More matches resolved (Thunder v Scorchers, NPL x2, WBBL 6 Nov) before reading any delay curve.
- Faster feed: Decimal Data is Cricket Australia's exclusive betting data partner (in-venue scouts, BBL/WBBL); free feeds are ~30 s behind the price.

## Update: snapshot to 12:35Z (4 T20 matches, 167 wickets and boundaries)
Matches: WBBL Strikers v Heat (Heat won), WBBL Thunder v Scorchers (Scorchers won), NPL Lions v Bolts (Lions won), NPL Kings v Gorkhas (in progress at the cut-off, no result). Tests and ODIs excluded: three-way markets and a different game.
- Lag (event-triggered average, eta.py): total move by +90 s is 5.1c; 87% already done when ESPN shows the ball; half done by 30 s earlier. Same answer as the 92-event run, so ESPN is about 30 s behind the price. The placebo (random times, random sign) stays within about 0.4c of zero and drifts slightly negative, so the real move is not noise.
- Delay curve (analyze.py, bid mid x 0.975 below the ask, hold to resolution, fills from real trades with queue ahead, 500-share cap): 1 to 10 fills per delay out of ~100 to 130 bids, spread over three resolved matches. Results swing from -100% to +142% return with no pattern by delay (anchor 0, ESPN as it is: +53% at 0 s on 10 fills, +23% at 5 s, +6% at 10 s, -56% at 20 s on 4 fills, +33% at 60 s on 7 fills; anchor 30, a feed at true event time: +142% at 0 s on 5 fills, +21% to +125% elsewhere). No verdict. At most 1 to 2% of events fill, and most fills come from the two WBBL games.
- So: the only solid finding is the lag. Whether the rule makes money at true event time needs many more fills, which means many more WBBL-sized games; BBL itself (12 Dec) will give that.

## Final status (17:40Z 5 Nov)
Hermes's last chunk (commit 4ac4a25b on claude/project-thread-aih58c, 15:10-17:30Z) adds nothing for the rule: its only ESPN T20 is Warriors v Boland (South African domestic), which has no Polymarket market, plus Zimbabwe A v Ireland A. Data between 12:35Z and 15:10Z was not committed (capture was paused and restarted), so Kings v Gorkhas has no result in our files. The 12:35Z results above are final for today: 167 events, four T20 matches, ESPN ~30 s behind the price, delay curve inconclusive. The chunk commit also added an accidental git index file (`idx`, 3 MB) in this folder, which should be removed.
