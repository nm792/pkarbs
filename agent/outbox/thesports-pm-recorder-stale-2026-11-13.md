# Reply to inbox #306 — TheSports Polymarket side: cause found, measured 16:12-16:14Z

Diagnosis only; no code, config or unit was changed (the two fixes below are class 4, filed in
`dialogue/APPROVALS.md` as open approval **#21** for the daily report).

## 1. Cause of the market-registration stop (REAL, still stopped)

- Live log `.../final-topics-32295b/log.jsonl`: last good `discover_pm` **2026-11-12T12:34:19Z**
  (`tokens=5694, new=0`); first `discover_pm_err` **2026-11-12T12:39:26Z**, error
  `<HTTPError 406: 'Not Acceptable'>`, repeating every ~5 min through **16:07:56Z** (still failing now).
  Live `markets.jsonl` mtime **12 Nov 12:13Z**, count frozen at 2,847 in every `counts` line on 13 Nov.
- **Root cause isolated by bisection against the exact endpoint** (`/events?tag_slug=...&active=true&closed=false`,
  same UA `pkarbs-thesports-trial/1.0`): `limit<=50 -> HTTP 200`, `limit>=51 -> HTTP 406`.
  Measured: 100/60/51 -> 406, 50/40/25/20 -> 200. The capture passes `limit=100`
  (`live/thesports/capture.py` `discover_pm()`), so **the gamma API raised its page cap to 50 on
  12 Nov ~12:39Z and every discover call has 406'd since.** Not a UA, not an Accept header, not `offset`,
  not a dead process — the capture unit is alive (uptime 5 d, `counts` lines current to 16:07:56Z).
- **Fix (class 4, approval #21):** in `discover_pm()` change `limit=100` to `limit=50` and the page stride
  `for off in range(0, 1000, 100)` to `range(0, 1000, 50)`, then restart the existing capture unit
  (397a, unchanged config). Revert: restore `capture.py.pre-gamma-limit-<stamp>` and restart.
  **A restart alone does NOT fix it** — the 406 is returned per request, so nothing was restarted today.

## 2. pmws: the RECORDER IS NOT STOPPED — the gap is the repo-side export gate

- Live `.../final-topics-32295b/pmws.jsonl`: 37 MB, newest row ms `1794586314458` = **2026-11-13T16:11:54Z**;
  capture `counts` shows pmws 168,365 (11:32Z) -> **180,971 (16:08Z)**, monotonically rising;
  share copy `share/pmws.jsonl.gz` mtime **13 Nov 16:01Z**, newest row inside **13 Nov 16:01:19Z**.
- The stale file the note measured is the repo slice `rn1/scores/thesports/final-topics-32295b-slim/pmws.jsonl.gz`:
  mtime **13 Nov 07:19:38Z**, newest row **12 Nov 05:36:45Z**, 130,981 rows. Cause: the exporter
  (`live/thesports/export_slim_32295_plumb.py`) copies pmws and then **deletes the copy when it exceeds
  950,000 B** (`SKIP ... > 950KB (1MB pre-push hook) ... project to rule on split or box+manifest route`),
  so once pmws outgrew ~950 KB the repo slice stopped being replaced and keeps its old content.
  This is an export-size gate, not a dead recorder — **no restart changes it.** The split/box+manifest route
  for pmws is a project ruling (the exporter asks for it in its own SKIP line); filed as an in-repo question
  in this reply's companion status line, not as a Nick approval.
- So the note's two stop times split: **market registration really stopped (406), pmws only looks stopped in
  the repo export (size gate), and is live on disk to 16:11Z.**

## 3. Can the 12 Nov Dota markets be re-paired from data already on disk? YES

`markets.jsonl` (live) holds **2,847 registered tokens through 12 Nov 12:13:43Z** and the repo slim copy holds
3,053 rows to the same timestamp, so the 12 Nov registrations (`z10-angryb`, `p-synaps`, `redjoh-pckcp`,
`oldblo-xe`) are still on disk and can be re-paired against `books_mid`/`ts_mqtt` without re-registration.
No rule is changed by doing so; the locked test D1 still needs its 40 paired games, and games after
12 Nov 12:13Z need approval #21 applied first.

## Status for `agent/status/thesports-trial.md` (due 17:00Z): written this pass, 16:14Z.
