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

## Faster-feed leads (web research 5 Nov, vendor claims, none tested)
- Decimal Data: Cricket Australia's exclusive betting data partner to 2031 (BBL, WBBL, domestic, home internationals), in-venue access and 120+ analysts (sportcal report). No public API, latency or price. Needs a sales email; a likely corporate-only model like GRID.
- Statscore ScoutsFeed: lists cricket; venue-sourced feed advertised at 1-2 s, TV-sourced 3-6 s, and its own docs call the 7-15 s TV-sourced type unsuitable for bookmakers. Delivery via AMQP/RabbitMQ or JSON. Price unpublished. Worth an email, and a trial request.
- Goalserve: cricket live-score plan $125 per month ($550 six months, $1,000 twelve months); ball-by-ball in the feature list; claims "within a second of action"; no websocket mention. The source of that data (TV or venue) is not stated, so it may be as late as ESPN. Test with a one-month plan only after a free-trial request.
- Roanuz: websocket push plus webhooks (unofficial doc); latency and price not found.
Test method for any of them: record the vendor feed alongside books.jsonl and run eta.py with the vendor events instead of ESPN; the question is whether half the move happens after the vendor's event, not before.
