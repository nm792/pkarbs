# Reachability check — 2026-10-29

Task `agent/TASK-reachability-check-2026-10-29.md` (approved by Nick 29 Oct 05:40Z). One curl per endpoint, honest UA `pkarbs-reachability/1.0 (contact nm@delphic.co)`, read-only. No loops/retries.

## Result: PASS — report written, one row per endpoint

| endpoint | HTTP status | bytes | first 200 bytes |
|---|---|---|---|
| https://www.hltv.org/results | 200 | 332671 | `<!DOCTYPE html> <html lang="en" data-client-country-iso="FI" data-impression-tracking-endpoint="https://ncuxt.hltv.org" data-ad-tag-allowed-cookies=...` |
| https://liquipedia.net/counterstrike/Main_Page | 403 | 2059 | `<!doctype html><html lang=en><meta name=viewport content="width=device-width,initial-scale=1"><meta charset=utf-8><meta name=robots content="noindex"><title>Liquipedia</title>...` |
| https://api.liquipedia.net/ | 200 | 1932 | `<!DOCTYPE html><html lang="en" dir="ltr"><head><meta charset="utf-8"><title>Home - Liquipedia DB</title>...` |
| https://api.sofascore.com/api/v1/sport/tennis/events/live | 403 | 48 | `{"error": {"code": 403, "reason": "Forbidden" }}` |

Every number above is measured from the four requests. A 403 is a recorded result, not a task failure (per the task's own pass/fail).

**Cleanup:** `/tmp/reach_body` removed. No reachability curl left running (only the code-0/race curls for the unrelated n324 MGM race remain, out of this task's scope). `ps` above; memory `free -m`: total 4056 MB.
