# thesports-trial status
state: running (capture-b active; 2h slim timer armed 2026-11-08; approved timer-fix applied 2026-11-09)
last export (UTC): 14:38:44Z
push_rc: 1

## 306 status, due 17:00Z — posted 16:14Z (diagnosis measured; no change applied)

- **Market registration: stopped by the gamma API page cap, not by the box.** Last good `discover_pm`
  12 Nov 12:34:19Z; `406 Not Acceptable` from 12 Nov 12:39:26Z, still failing at 16:07:56Z.
  Bisection on the live endpoint: `limit<=50 -> 200`, `limit>=51 -> 406` (100/60/51 = 406; 50/40/25 = 200).
  `discover_pm()` sends `limit=100`. **Fix = 2-line code change, filed as class-4 open approval #21**
  (`dialogue/APPROVALS.md`): `limit=100 -> 50`, stride `range(0,1000,100) -> range(0,1000,50)`, then restart the
  existing capture unit (397a). Revert: restore the pre-edit copy + restart. A restart alone does not fix it.
- **pmws: recorder LIVE, export slice gated.** Live `pmws.jsonl` newest row 13 Nov 16:11:54Z; capture counts
  168,365 (11:32Z) -> 180,971 (16:08Z); `share/pmws.jsonl.gz` rebuilt 16:01:19Z. The repo slice
  `final-topics-32295b-slim/pmws.jsonl.gz` is old (mtime 13 Nov 07:19:38Z, newest row 12 Nov 05:36:45Z)
  because the exporter deletes any pmws copy over 950,000 B (1 MB pre-push hook) and asks the project to rule
  on split vs box+manifest. **Not a stopped recorder; no restart applies.** Project ruling needed in-repo.
- **12 Nov markets re-pairable: YES** — 2,847 tokens (live) / 3,053 rows (repo slim) through 12 Nov 12:13:43Z,
  `books_mid` current to 13 Nov 15:00Z; the four 12 Nov Dota registrations can be re-paired from disk.
  D1 still needs 40 paired games; post-12 Nov games need #21.
- **No unit restarted, no file edited this pass** (class 4 not applied without the daily approval).
  Full reply: `agent/outbox/thesports-pm-recorder-stale-2026-11-13.md`.
