# RETEST: RapidAPI "Reuters API" timestamps (Step 1 redo), URGENT

From: Claude, PK arbs project, on Nick's instruction (14 Nov 04:45Z: "so you tested it incompetently"). Status: DONE — retest complete; usable first-publication timestamp verdict: no. Supersedes the NO verdict in outbox/rapidapi-reuters-nvda-timestamp-2026-11-13.md until this retest reports. Standard: feeds/STANDARD-feed-latency-test.md v1 (cited, not restated).
Key: same store as before, never printed or committed. Budget: <= 300 calls total, pace >= 0.5 s, browser User-Agent on every request (Cloudflare 1010 otherwise).

## Why the first run is not accepted
- The 3 `/details` probes used article URLs that were GUESSED slugs, not links the API itself returned. `/details` then returned other articles (probably fuzzy matching). That tests our URLs, not the API.
- Only `published_at` and `updated_at` were read. The full JSON was not searched for other time fields, and the article page itself was not checked.

## Exact calls (log HTTP status, ms, and save the full raw JSON for each; keep key out)
A. `GET /latest`: save the full response. List EVERY key at every level (not only published_at). Note any field holding a time, HTML, or an article id/slug.
B. `GET /search` with the query for the NVDA story ("Jensen Huang steps down"); also 4 other 12-13 Nov stories picked from /latest. Take each result's `link` EXACTLY as returned (verbatim, no edits, no re-slugging).
C. `GET /details?url=<that verbatim link>` for each link from B. For each, check the returned title matches the one /search gave. Record published_at, updated_at, and every other field; search the whole JSON (and any html/body string) case-insensitively for: published, publish, datePublished, date_published, first, created, time, article:published_time, ld+json. Also try /details with the link as a path only (e.g. /world/...) and with the full https://www.reuters.com... form, if the first form fails to match. Pick the form that returns the matching title and record which it was.
D. Page check: fetch each article page directly from reuters.com with a browser User-Agent (read-only, 1 request per article, 10 articles max). Extract `<meta property="article:published_time">`, `article:modified_time`, and JSON-LD `datePublished` / `dateModified`. If blocked (DataDome/403), say so and stop D; do not try to evade.
E. Read the RapidAPI endpoint documentation (the listing's endpoint pages / playground examples) and write down the documented parameter names, the identifier each endpoint takes, and example values. If the server cannot reach rapidapi.com, say so.

## Test set
At least 10 articles with a known story time: the NVDA/Huang story, plus 9 others from /latest and /search dated 12-14 Nov. For each, report: API published_at (raw), page published_time (if D worked), difference in seconds, and whether the API time is minute-rounded.

## Verdict (write outbox/rapidapi-reuters-RETEST-2026-11-14.md)
Line: "Scraper carries a usable first-publication timestamp to the second: yes / no", with the table above and one line each on: correct way to call /details, and whether a second-precision time exists ANYWHERE in the response or the page.
If YES: go to Step 2 as in the original task (poll /latest, lag median/p90/max; median < 10 s gates a STANDARD v1 pre-registration and independent audit). If NO: stop.

## Deadline
Post status in agent/status by 05:45Z even if unfinished; verdict file by 06:15Z. Run it right after item (2) of P12 (#317) if that is still open; it is a short run, ~60-100 calls, no capture, no new collector.
