# thesports-trial status
state: running (capture-b active; 2h slim timer armed 2026-11-08; approved timer-fix applied 2026-11-09)
last export (UTC): 18:55:05Z build (60e644526584), landed 21:45:47Z as b0358c9113
push_rc: 1 (non-fast-forward race on the direct push; additive landing on tip succeeded)

## A50 volume growth investigation (19 Nov 2026)

- Read-only du pass 1 at 04:09:35Z: VOL2 used 83,373,522,944 B, free 16,330,252,288 B. Largest paths: `pkarbs` 71,869,805,056 B; `pkarbs-ps-step2` 2,278,913,232 B; `swapfile2` 2,147,483,648 B; `nt_live_fire` 1,180,860,097 B.
- Read-only du pass 2 at 04:16:47Z: VOL2 used 84,164,714,496 B, free 15,539,060,736 B. Largest paths: `pkarbs` 72,622,761,864 B (+752,956,808 B); `pkarbs-ps-step2` 2,278,913,232 B (0 B); `swapfile2` 2,147,483,648 B (0 B); `nt_live_fire` 1,181,061,232 B (+201,135 B). The dominant directory delta is `pkarbs`.
- `find -mmin -30` and process snapshot at 04:16:47Z showed active data under `pkarbs/thesports/final-topics-32295b`: `books.jsonl` 23,292,975,394 B, `ts_mqtt.jsonl` 16,970,673,134 B, `trades.jsonl` 995,037,907 B; `share/books.jsonl.gz.tmp` 2,926,964,670 B. `fuser` identified PID 2489797 (`capture.py`, started 14 Nov 03:30:03Z) holding `books.jsonl`, `ts_mqtt.jsonl`, and the tmp gzip. PID 2271688 (`pm_trades_capture.py`) also runs against this store.
- Attribution: the TheSports capture/export path is the clear active writer in the largest growing directory; PID 2489797 is directly writing books and MQTT and its concurrent share gzip. These readings establish the dominant growth location, but do not apportion the full 7m12s increase among individual streams.
- No gzip, move, trim, or delete was performed. At the second sample free space was 15,539,060,736 B, about 0.54 GB above the stated 15 GB recorder guard. The observed 0.79 GB increase over 7m12s suggests the guard could be reached within minutes if the same rate continues; exact crossing time is uncertain because the sample overlaps active writes. No trim was authorized by this read-only task.

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

## P10 status, posted 2026-11-13 22:09Z (owed within 60 min of the 20:07Z URGENT; LATE - deadline 21:07Z, IT flagged the miss 21:10Z)

- **Diary gap closed:** dota2/csgo/lol/tennis for 12 and 13 Nov fetched **21:25:08-21:25:10Z**,
  committed `b17b066da4` (21:41:07Z), exported. Outbox reply:
  `agent/outbox/thesports-diary-gap-and-split-ruling-2026-11-13.md`.
- **pmws split applied** to `live/thesports/export_slim_32295_plumb.py` in `b17b066da4`
  (diff sha256 `69d25fd38240...`; backup `.pre-pmws-split-20261113T2138Z`). Parts NOT on origin yet:
  `pmws.jsonl.gz` is still 1,026,005 B because the in-flight 2h build (pid 1182958, started 20:31Z,
  mid-index 22:05Z) predates the edit; next build produces `pmws.part*` + manifest.
- **2h export since 64a2a79757: cause = non-fast-forward push race** (log: 13:08:56Z +12,909 rc=1;
  18:55:03Z +17,723 rc=1, both rejected). Stranded 18:55Z build landed additively
  **21:45:47Z `b0358c9113`** (+17,718 files, 0 deleted, newest slim ts_mqtt 17:05:32Z).
- Nothing restarted, no capture logic changed this run.
