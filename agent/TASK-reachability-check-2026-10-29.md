# Task for the server agent: tiny reachability check (4 endpoints, one curl each)

From: Claude in the "PK arbs" project thread "Match rn1 trades to live scores" (29 Oct 2026).
Approved by Nick in the thread on 29 Oct 2026 (05:40Z).
Status: DONE (report run + committed 2026-10-29, reports/reachability/reachability-2026-10-29.md)

## Hard rules
- One `curl` per endpoint. No loops, no retries, no crawling.
- Honest descriptive User-Agent only: `pkarbs-reachability/1.0 (contact nm@delphic.co)`. Do not spoof a browser.
- Runtime limit 2 minutes for the whole task: `timeout 120`.
- Read-only. No keys, no logins, no orders.
- Keep raw response bodies out of git. Only the report is committed.

## Question
Which of these four endpoints answer a plain, honestly identified request from the server?

## Endpoints
1. https://www.hltv.org/results
2. https://liquipedia.net/counterstrike/Main_Page
3. https://api.liquipedia.net/
4. https://api.sofascore.com/api/v1/sport/tennis/events/live

## Pass / fail (fixed before run)
- PASS: the report file is written with a row for each endpoint, containing HTTP status, response size in bytes, and the first 200 bytes of the body.
- FAIL: the report is missing, or any row is missing. A 403, 429 or other error status is a recorded result, not a failure of the task.

## Procedure
```
OUT=reports/reachability/reachability-2026-10-29.md
mkdir -p reports/reachability
UA='pkarbs-reachability/1.0 (contact nm@delphic.co)'
for u in https://www.hltv.org/results https://liquipedia.net/counterstrike/Main_Page https://api.liquipedia.net/ https://api.sofascore.com/api/v1/sport/tennis/events/live; do
  timeout 30 curl -sS -m 25 -A "$UA" -o /tmp/reach_body -w '%{http_code} %{size_download}' "$u"
  head -c 200 /tmp/reach_body | tr '\n' ' '
  rm -f /tmp/reach_body
done
```
Write each row to $OUT as: endpoint | HTTP status | bytes | first 200 bytes.

## Cleanup
Remove /tmp/reach_body. Run `ps` and `free -m` after and state the output in the report. Kill any curl still running.

## Labels
Every number in the report is measured from these four requests. No estimates.
