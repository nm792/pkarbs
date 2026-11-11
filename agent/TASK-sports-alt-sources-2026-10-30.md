# Task for the server agent: alternative in-play score sources (NBA play-by-play, esports APIs), robots first

From: Claude in the "PK arbs" project thread "Match rn1 trades to live scores" (30 Oct 2026).
Requested by Nick in the thread: find another CS2 score source, or a similar in-play market with historical score data reachable.
Status: DONE — 2026-10-30 (NBA pbp unreachable 000 / ESPN robots-403 / PandaScore keyed; report reports/alt-sources/alt-sources-2026-10-30.md)

## Why these hosts
rn1's maker markout ranking in the 22-29 Oct window (step 4, measured at 60 s on the top 500 markets, % of USDC):
tennis +1.83%, CS2 +1.65%, soccer +0.58%, US sports +0.39%. US sports here is NBA, NFL, NHL, MLB and college football, and NBA is the largest slice (604 slugs). So NBA is the first similar market to test, and esports is the next candidate for CS2 (it is the only other esports rn1 trades, and it lacks a score source).

## Hard rules
- Honest User-Agent only: `pkarbs-research/1.0 (contact nm@delphic.co)`. Do not spoof a browser.
- Robots first. For each host, fetch `/robots.txt` before any other path. If it disallows the path you need, stop on that host and record it.
- No keys, logins, or sign-ups. If a source needs a key, make one unauthenticated request to record the response (expected 401 or 403), then stop there.
- If any response is 403, 429, or 5xx, record it and stop on that host. Do not retry, and do not try another route to get past it.
- Pacing: at least 5 seconds between requests.
- Request budget: at most 20 requests in total, and at most 4 per host (robots plus up to 3 pages).
- Runtime limit 10 minutes: `timeout 600`. Memory cap 512 MB: `systemd-run --scope -p MemoryMax=512M -p MemorySwapMax=0`.
- Read-only. Raw JSON or HTML goes to `shadow/alt-sources-raw/`, which is not committed.

## Hosts
1. https://site.api.espn.com/ : NBA scoreboard for 22-29 Oct 2026, then one completed game's summary (`/apis/site/v2/sports/basketball/nba/summary?event=<id>`), checking for play-by-play with clock times and scores.
2. https://cdn.nba.com/ : the public live play-by-play JSON for one completed game in the window, if robots allows it.
3. https://api.pandascore.co/ : one unauthenticated request for CS2 matches, to record the response (expect 401). Do not request a token.

## Pass / fail (fixed before the run)
- PASS: at least one of the NBA hosts (1 or 2) returns play-by-play with clock times and running scores for one game in 22-29 Oct. Record the URL, the number of plays, and the first and last play.
- FAIL: neither NBA host gives play-by-play for a game in the window, or the report is missing.
- The PandaScore row is recorded either way. A 401 is a result, not a failure.

## Output
Report: `reports/alt-sources/alt-sources-2026-10-30.md`, with a request log (URL, status, bytes, delay), one row per host (robots result, status, whether play-by-play is present, why not), the PASS/FAIL line, and an overall verdict on which source to use next.

## Labels
Every number is measured from the fetched responses. Do not report estimates.

## Cleanup
Kill any process you started. Run `ps` and `free -m` after and state the output in the report.
