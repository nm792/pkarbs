# Task for the server agent: coverage check for tennis and CS2 score sources (robots.txt first, then a few pages)

From: Claude in the "PK arbs" project thread "Match rn1 trades to live scores" (30 Oct 2026).
Requested by Nick in the thread: find score sources for rn1's matches (tennis and CS2) without asking him.
Status: DONE — 2026-10-30 (coverage report: all tennis/CS2 sources JS-rendered; no static game-level scores served; report reports/coverage/coverage-2026-10-30.md)

## Question
For rn1's 22-29 Oct 2026 matches, does any public source carry game-level tennis scores (ATP, Challenger, WTA) and round-level or map-level CS2 scores, and is it allowed to fetch?

Coverage matters more than reachability. rn1's tennis markets are mostly ATP (268 slugs), WTA (143), and ITF (60), so a WTA-only source does not cover most of the set.

## Hard rules
- Honest User-Agent only: `pkarbs-research/1.0 (contact nm@delphic.co)`. Do not spoof a browser.
- Robots first. For each host, fetch `/robots.txt` before any other path. If it disallows the path you need, stop on that host and record it. Do not fetch that path.
- No keys, logins, or sign-ups. If a source needs a key or account, record that and stop there.
- If any response is 403, 429, or 5xx, record it and stop on that host. Do not retry, and do not try another route to get past it.
- Pacing: at least 5 seconds between requests.
- Request budget: at most 4 requests per host (robots plus up to 3 pages), and at most 24 requests in total.
- Runtime limit 15 minutes: `timeout 900`. Memory cap 512 MB: `systemd-run --scope -p MemoryMax=512M -p MemorySwapMax=0`.
- Read-only. Raw HTML goes to `shadow/coverage-raw/`, which is not committed.

## Hosts
Tennis:
1. https://www.tennisabstract.com/ (look for an ATP or Challenger match in 22-29 Oct, then check whether its page lists set and game scores)
2. https://www.wtatennis.com/ (look for a WTA match in 22-29 Oct, then check whether its page lists set and game scores)
3. https://www.ultimatetennisstatistics.com/ (same check as Tennis Abstract, if robots allows it)

CS2:
4. https://www.bo3.gg/ (look for a CS2 match in 22-29 Oct, then check whether its page shows map scores and round scores)
5. https://www.hltv.org/ is OUT. Its robots.txt disallows /results and /matches. Do not fetch it.

## Pass / fail (fixed before the run)
- PASS for tennis: at least one ATP or Challenger match and at least one WTA match in 22-29 Oct have game-level set scores on a page the source serves, with the page's URL and parsed scores recorded.
- PASS for CS2: at least one CS2 match in 22-29 Oct has map scores and round scores on a page the source serves, with the URL and parsed scores recorded.
- Each host also gets a row: robots result, page status, whether the needed scores are present, and why not if they're missing.
- FAIL: the report is missing, or a host is recorded without its robots result.

## Output
Report: `reports/coverage/coverage-2026-10-30.md`, with a request log (URL, status, bytes, delay), one row per host, and the PASS/FAIL line for tennis and for CS2. Summary CSV: `reports/coverage/coverage-2026-10-30.csv`, one row per parsed match (source, date, tour or league, players or teams, scores as found).

## Labels
Every number is measured from the fetched pages. Do not report estimates.

## Cleanup
Kill any process you started. Run `ps` and `free -m` after and state the output in the report.
