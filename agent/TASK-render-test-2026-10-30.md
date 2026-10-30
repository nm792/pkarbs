# Task for the server agent: 3-match headless-render test for tennis and CS2 scores (robots first)

From: Claude in the "PK arbs" project thread "Match rn1 trades to live scores" (30 Oct 2026).
Requested by Nick in the thread: find a historical score source for rn1's tennis and CS2 matches.
Status: DONE — 2026-10-30 (render-test PASS 2/3: WTA 6-2 6-2 + ATP 7-5 6-2 in-window scores parsed; bo3 renders but no map scores; report + raw HTML committed)

## Question
The static HTML of the robots-allowed score sites (wtatennis.com, bo3.gg, tennisabstract.com, ultimatetennisstatistics.com) carries no set, game, map or round scores (see reports/coverage/coverage-2026-10-30.md). Once the pages are rendered in a headless browser, do they carry those scores for 3 completed matches in 22-29 Oct 2026?

## Hard rules
- Honest User-Agent only: `pkarbs-research/1.0 (contact nm@delphic.co)`. Set it on the browser context. Do not use stealth or fingerprint evasion.
- Robots first. For each host, fetch `/robots.txt` with curl before opening any page in the browser. If robots disallows the page path, skip that host and record it.
- Pages to render: at most 3 in total, at most 2 per host. No crawling, no following links beyond the single match page per match.
- Use one browser context and one page at a time. Wait at least 5 seconds between page loads.
- Stop immediately on any HTTP 403, 429 or 5xx, or a bot-check challenge page, and record it. Do not retry, and do not switch route to get past it.
- No keys, logins, or sign-ups.
- Runtime limit 5 minutes: `timeout 300`. Memory cap 512 MB: `systemd-run --scope -p MemoryMax=512M -p MemorySwapMax=0`. One process only.
- Chromium is at `/opt/pw-browsers/chromium` if Playwright is installed. Use `chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] })`. Do not run `playwright install`.

## Matches
- 2 tennis matches from 22-29 Oct 2026: one WTA (wtatennis.com) and one ATP or Challenger (tennisabstract.com). Prefer matches whose players appear in rn1's market slugs, for example `wta-rybakin-fernand-2026-10-25`, if you can read that list. Otherwise take any completed match in the window.
- 1 CS2 match from 22-29 Oct 2026 on bo3.gg, from its matches list (`/matches`), a completed match.

## Pass / fail (fixed before the run)
- PASS: at least 2 of the 3 rendered pages contain parsed final scores (tennis: set and game scores; CS2: map scores and round scores).
- FAIL: fewer than 2 pages with parsed scores, or any 403, 429, 5xx or challenge page.
- Forward logging is unaffected. Do not touch the Polymarket WebSocket logger.

## Output
- Raw rendered HTML for each page, saved to `reports/render-test/raw/` and committed. These are the project's raw data.
- Report: `reports/render-test/render-test-2026-10-30.md`, with the request log (URL, robots result, status, bytes, delay), each page's parsed scores (or why not), and the PASS/FAIL line.
- Summary CSV: `reports/render-test/render-test-2026-10-30.csv`, one row per parsed match (source, date, league, players or teams, scores as found).

## Labels
Every number is measured from the rendered pages. Do not report estimates.

## Cleanup
Close the browser. Kill any process you started. Run `ps` and `free -m` after and state the output in the report.
