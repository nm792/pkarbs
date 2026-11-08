# AFL: strategic build for the 2027 season (3 Nov 2026)

**Polymarket today (measured, gamma series 12563/12564):** listed from 8 Aug 2026. 36 men's games, $126k total (one game $96k); AFLW 101 games, $8k. Nick expects volume to become large; we prepare for 2027 rather than trade it now.

**2027 dates (afl.com.au):** Opening Round scrapped. Round 1 runs Wed 17 Mar to Sun 21 Mar 2027 (Sydney v Geelong at the SCG opens), later than usual because of the MCG 150th-anniversary Test 11-15 Mar. Gather Round 8-11 Apr (SA). Home-and-away ends round 24, Sun 30 Aug. Grand Final Sat 3 Oct 2027. Preseason dates not yet confirmed (normally late Feb to early Mar).

**Score data (tested from this container):**
- ESPN site API works: `site.api.espn.com/apis/site/v2/sports/australian-football/afl/scoreboard?dates=YYYYMMDD` and `/summary?event=<id>`. Each summary lists every goal and behind with quarter, quarter clock and running score (e.g. 52 scoring plays in game 1133666). Data checked for 2019, 2021-2026 games. **No wall-clock time** (`wallclockAvailable: false`), so historical plays cannot be aligned to price to the second.
- Squiggle API, the AFL's own API (aflapi.afl.com.au / api.afl.com.au) and fixturedownload.com are blocked by this container's network proxy. Squiggle has free fixtures, results and model tips; it is worth asking for if we want it.
- Live latency is unmeasured: there are no AFL games until March. We measure it on the 2027 preseason or round 1 by polling ESPN every 2 s and logging receipt time, with the Polymarket sports websocket alongside.

**Jump model (no backtest yet):** fit from ESPN plays 2019-2026 (about 1,600 games): win probability from margin x time left (normal remaining-margin model, like the NBA one in winmodels/us), and the jump per goal (6 points) or behind (1 point). This can be done offline at any time before March.

**Plan:**
1. Offline before Feb 2027: pull ESPN AFL plays 2019-2026, then fit the win-probability and jump model.
2. Preseason or round 1 (from 17 Mar 2027): live capture of ESPN plus Polymarket prices to measure feed latency against price.
3. Monitor Polymarket AFL volume monthly in the calendar refresh; go to paper trading only if volume per game reaches about $1M or more.
