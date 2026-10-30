# Task for the server agent: tennis score source probe (one curl each, honest User-Agent)

From: Claude in the "PK arbs" project thread "Match rn1 trades to live scores" (30 Oct 2026).
Requested by Nick in the thread: find a historical tennis score source for rn1's 22-29 Oct matches.
Status: DONE — 2026-10-30 (probe PASS)

## Note on the protocol
This is a read-only probe of eight URLs. It runs next to the HLTV task (agent/TASK-hltv-cs2-rounds-2026-10-29.md), which is still OPEN. The HLTV task is not waiting on this one, and this one puts no load on the server. Run it after the HLTV task finishes, not in parallel.

## Question
Which of these tennis sources answer a plain, honestly identified request from the server?

## Hard rules
- One `curl` per URL. No loops, no retries, no crawling.
- Honest User-Agent only: `pkarbs-research/1.0 (contact nm@delphic.co)`. Do not spoof a browser.
- If a URL returns 403 or 429, record it and move on. Do not retry it, and do not try another route to get past it.
- Runtime limit 2 minutes for the whole task: `timeout 120`.
- Read-only. No keys, no logins.

## URLs
1. https://www.atptour.com/en/scores/current
2. https://www.wtatennis.com/
3. https://www.flashscore.com/
4. https://www.livescore.com/
5. https://www.espn.com/tennis/scoreboard
6. https://www.tennisabstract.com/
7. https://www.ultimatetennisstatistics.com/
8. https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/README.md

## Pass / fail (fixed before the run)
- PASS: the report file is written with one row per URL, containing HTTP status, response size in bytes, and the first 200 bytes of the body.
- FAIL: the report is missing, or any row is missing. A 403, 429, or 000 (no connection) is a recorded result, not a failure of the task.

## Procedure
```
OUT=reports/tennis-probe/tennis-probe-2026-10-30.md
mkdir -p reports/tennis-probe
UA='pkarbs-research/1.0 (contact nm@delphic.co)'
for u in <the 8 URLs above>; do
  timeout 30 curl -sS -m 25 -A "$UA" -o /tmp/tennis_body -w '%{http_code} %{size_download}' "$u"
  head -c 200 /tmp/tennis_body | tr '\n' ' '
  rm -f /tmp/tennis_body
done
```
Write each row to $OUT as: URL | HTTP status | bytes | first 200 bytes.

## Cleanup
Remove /tmp/tennis_body. Run `ps` and `free -m` after and state the output in the report. Kill any curl still running.

## Labels
Every number in the report is measured from these eight requests. No estimates.
