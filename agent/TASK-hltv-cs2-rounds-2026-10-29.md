# Task for the server agent: small HLTV pull of CS2 map and round scores for rn1's window (22-29 Oct 2026)

From: Claude in the "PK arbs" project thread "Match rn1 trades to live scores" (29 Oct 2026).
Requested by Nick in the thread (29 Oct 2026, 13:49Z): find score sources for rn1's CS2 and tennis matches.
Status: DONE — 2026-10-29 (HLTV stopped at robots.txt, per hard rule)

## Question
For CS2 matches in the window 22-29 Oct 2026 that HLTV lists, can we get per-map scores and, for the matches we fetch, per-round scores, at polite pacing?

## Hard rules
- One process, one run. No parallel requests. No retries on any error.
- Honest User-Agent only: `pkarbs-research/1.0 (contact nm@delphic.co)`. Do not spoof a browser.
- Before anything else, fetch https://www.hltv.org/robots.txt. If it disallows `/results` or `/matches`, stop and report. Do not fetch those paths.
- Pacing: at least 5 seconds between requests.
- Request budget: at most 8 results pages (one per day, 22 to 29 Oct) and at most 30 match pages. Total at most 38 requests.
- Stop immediately on any HTTP 403, 429 or 5xx, and report it. Do not try again.
- Runtime limit 20 minutes: `timeout 1200`. Memory cap 512 MB: run under `systemd-run --scope -p MemoryMax=512M -p MemorySwapMax=0`.
- Read-only. No accounts, no logins, no keys.
- Raw HTML goes to `shadow/hltv-raw/`, which is not committed. Only the summary and the report are committed.

## Pass / fail (fixed before the run)
- PASS: at least 20 match pages were fetched and each has a per-map score parsed, AND the report file lists every request with its status code and byte count.
- FAIL: fewer than 20 match pages with a parsed map score, OR any 403/429/5xx, OR a disallowed robots.txt path.
- Round-level scores are recorded when present, but they are not part of the pass rule. Report how many matches had them.

## Output
- Summary CSV: `reports/hltv/cs2-maps-2026-10-22-to-29.csv`, one row per map: match id, date, team A, team B, map name, map score A, map score B, round scores if present.
- Report: `reports/hltv/cs2-maps-2026-10-22-to-29.md`, with a request log (URL, status, bytes, delay), the pass/fail result, and the count of matches with round scores.

## Labels
Every number in the report is measured from the fetched pages. Do not report estimates.

## Cleanup
Kill any process you started. Delete nothing that is not yours. Run `ps` and `free -m` after and state the output in the report.
