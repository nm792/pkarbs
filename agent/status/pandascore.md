# status: PandaScore low-latency feed (v2) - RUNNING, first capture landed 13 Nov 15:11Z

Updated: 2026-11-13 15:17Z UTC. Approval: inbox `2026-11-13-pandascore-capture-APPROVED.md`
(Nick yes 14:44:29Z; task `TASK-pandascore-trial-2026-11-12.md` v2).

- **Token:** present — `/root/API_KEYS/pandascore/.env`, mode 600, `PANDASCORE_ACCESS_TOKEN`
  (51 bytes, supplied 13 Nov). **`/etc/pkarbs/pandascore.env` could not be written**: the
  terminal refuses `/etc` writes in unattended runs (consent gate, no user present), so the
  client falls back to the API_KEYS store — code checks `/etc/pkarbs/pandascore.env` first,
  then the API_KEYS file (reorder the moment an interactive run can write `/etc`).
  Token verified absent from every log/status/data file (grep, 0 hits) and never in a URL log.
- **Client:** `live/pandascore/ll_capture.py` (214 lines, `py_compile` OK), tmux session
  `pandascore`, pid 212720, started **15:12:29Z** (first process 15:11:11Z, restarted to add
  a per-row gzip flush). Discovery every 60 s with Bearer header on the low-latency feed list;
  CS2 (`cs-go`) + Dota 2 only, LoL skipped; one socket per match at/after `opens_at`;
  close codes handled per task (1000 stop, 4004 re-check, 4001/4003/4029 log-and-stop,
  1xxx/no-code backoff 1..30 s); 5-min silence logged, socket never killed on a timer.
- **Sockets:** 10 matches connected at 15:12:29Z (6 CS2, 4 Dota 2), one per match, within
  the 3-per-match limit.
- **Output:** `/vol2/pandascore/raw/pandascore_<YYYYMMDDHH>.jsonl.gz` (gzip, flush per row,
  closed at UTC hour rollover) + `/vol2/pandascore/events.jsonl.gz`.
  **45 rows by 15:13Z; first row `kind=hello`** for match 1791798 — first capture of the day
  (task deadline: first capture today) and every message logged with recv_ns, sha1,
  updated_at, available_fields, raw payload.
- **Disk:** free at start `/` 17,564,192,768 B (55%) — above the 15 GB floor; auto-stop
  guard in code writes `events` `kind=stopped` and exits at <=15 GB.
  **Same CRITICAL as goalserve: `/vol2` resolves to the root volume** (`findmnt -T /vol2` ->
  `/dev/sda1` on `/`), not a mounted disk; the 98 GB data disk sits at
  `/mnt/HC_Volume_107257520`. Path is what the task names; nothing moved; IT to rule.
- **MB/day:** first-hour measure due ~16:12Z (file size + row count of hour 2026111315).
- **Next status:** 15:47Z, 16:17Z while anything is open; capture verified by 16 Nov 12:00Z
  (BLAST Slam Dota 17 Nov); trial ends 1 Dec.

## Dota 2 coverage 16:15Z (inbox #305; posted 16:10Z, within the 16:15Z deadline — bounded counts, no rule changed)

Method: read-only parse of `/vol2/pandascore/raw/pandascore_*.jsonl.gz` (tolerant reader: hour-16 file is still
open, `EOFError` handled) and `/vol2/pandascore/events.jsonl.gz`; PM markets from the public gamma search API.
Script `/root/_dota_counts.py`, raw output `/root/_dota_counts_out.json`. No rule, threshold or socket behaviour touched.

1. **Sockets since 15:12:29Z: 13 matches touched (13 `hello` + 2,804 `status` rows by 16:1xZ); 5 of them Dota 2
   (`dota-2`), 8 CS2.** Dota sockets: `1791798` Froglings vs PuckChamp, `1793318` PARIVISION vs Yellow Submarine,
   `1785771` Team Allied vs potn9ki — all connected 15:12:29Z; `1806970` Team Liquid vs LGD Gaming and
   `1785772` Team Synapse vs Time to Sleep — connected 15:45:37Z. **4 of the 5 Dota matches carry a Polymarket
   Game-N-Winner / Match-Winner market matched on team names: Froglings vs PuckChamp (Game 1 0.9995, Game 2 0.93),
   PARIVISION vs Yellow Submarine (Game 1 closed 1/0, Game 2 0.9995), Team Allied vs potn9ki (Game 1 0.875,
   Game 2 0.585), Team Liquid vs LGD Gaming (Game 1 0.625, Game 2 0.605). `Team Synapse vs Time to Sleep` has NO
   Polymarket listing — 1 of 5 unpaired (80% pairing rate observed).**
2. **Dota state changes captured (diffed per `match_id` across consecutive `status` payloads; `game_timer` and
   net-worth drift excluded), events = per-side field changes:**
   - `1793318` PARIVISION vs Yellow Submarine (15:12:29Z-15:50:46Z): **kills 61** (28 + 33), **towers 12**,
     **barracks 4**, **roshans 1**.
   - `1791798` Froglings vs PuckChamp (15:12:29Z-16:06:59Z): **kills 38**, **towers 17**, **barracks 11**,
     **roshans 9**.
   - `1785771` Team Allied vs potn9ki (15:12:29Z-16:06:59Z): **kills 58**, **towers 14**, **barracks 6**,
     **roshans 9**.
   - `1806970` Team Liquid vs LGD Gaming and `1785772` Team Synapse vs Time to Sleep: **0 state changes in the
     window** (hello / first status only before their matches progressed).
   Totals: 3 Dota matches with real state changes, **157 kill-side changes, 43 tower, 21 barracks, 19 roshan**.
   CS2 payloads carry a different field shape and report 0 diffs under this Dota field set — CS2 is out of this
   note's scope and is not claimed. Not analysed as "sim on real data" — counts only.
   **Polymarket price coverage within +/-60 s: NOT COMPUTED.** No PM price/trade row source for esports markets was
   located on Prime this pass (the task names "the PM recorder" without a path; `pkarbs live/` holds no Polymarket
   price file from today). Blocker stated, not guessed: name the PM recorder path and this pass runs in minutes.
3. **ESTIMATE (not a fit): 5 Dota sockets / 4 PM-paired matches in the first 54 min of capture. At that observed
   rate, ~10 PM-paired distinct Dota matches need ~2-3 h of continued slate (i.e. this evening) and ~30 priced
   Dota events follow at ~3 priced markets per BO3 — ASSUMPTIONS: PM keeps listing 4/5 in-play Dota matches,
   the evening slate runs at the observed rate, and price coverage (point 2's blocker) is satisfied, which is
   unverified. BLAST Slam from 17 Nov is the dependable tier-1 source for the match-clustered CI. Rate rests on
   54 minutes of observation — thin.**

**First-hour MB (owed ~16:12Z):** hour-15 file `pandascore_2026111315.jsonl.gz` = 330,887 B for 15:12-16:00Z
(2,500 rows) -> **~7.9 MB/day gz projected**, far under any cap.

**Disk (P7): the capture still writes to root** (`/vol2` is a plain directory on the root volume, not a mount;
`findmnt -T /vol2` -> `/`). The off-root move is filed as class 4 in `dialogue/APPROVALS.md` (open approval #20,
(filed 16:10Z): repoint `OUT`/`EV` in `live/pandascore/ll_capture.py` to
`/mnt/HC_Volume_107257520/pkarbs/pandascore/`, move the two hour files, restart, delete the root copies only after
row counts match. Root free 17.56 GB (above the 15 GB floor), so waiting for the daily approval loses nothing.
Revert: restore the pre-edit copy and point the paths back.
## P8 part 2 - gamma limit=50 APPLIED, PM market registration live again (13 Nov 17:06Z; OPEN row P8; IT reply eb3abacd ruled approval #21 Type A, clause 22A)

- **Change** (`live/thesports/capture.py`, `discover_pm()` only, 3 lines): `limit=100 -> 50`, page stride `range(0,1000,100) -> range(0,1000,50)`, and the companion break threshold `len(r) < 100 -> len(r) < 50`. The threshold is the ONE line beyond the filed spec: with only the two spec lines a full 50-row page reads `< 100`, so pagination stops after page 1 and the stride change does nothing past offset 0. The reviewer can strike it if unwanted. `py_compile` OK.
- **Backup / revert:** `live/thesports/capture.py.pre-limit50-20261113T170314Z`, sha256 `e277381c826c0ad43fe4a7bd1595a09f7615ab78990765d4130258c21f7b9c54` (byte-identical to the pre-edit blob). Revert = restore that copy, restart the unit.
- **Restart:** old `timeout 552000 python3 ... capture.py` (pids 2818604/2818605, up since 8 Nov 00:42Z) stopped; `thesports-capture-b.service` started **17:06:03Z**, MainPID 465179, `is-active` = active. Restart gap about 70 s.
- **200 discover line:** `log.jsonl` 17:06:10Z `{"what":"discover_pm","tokens":216,"new":216}` - success rows only (errors are separate `discover_pm_err` rows); the last `406 Not Acceptable` was 16:58:36Z.
- **Registration counter:** `markets.jsonl` 2,847 -> **3,161 rows** (+314) by 17:06:10Z - registration is moving again.
- **Other streams after the restart:** books newest 17:06:54Z, pmws 17:06:53Z, ts_mqtt 17:05:32Z - all live; no other stream was stale.
- **Not changed:** no other line of the file. The relaunch keeps the original `timeout 552000`, which expires 14 Nov about 09:06Z with no restart guard anywhere on the box (no cron or unit references capture.py) - flagged as one TO-IT line, not touched here.
