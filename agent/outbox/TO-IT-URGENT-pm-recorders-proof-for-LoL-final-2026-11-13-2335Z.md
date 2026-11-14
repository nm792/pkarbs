# Reply to #315 — PM recording proof for the LoL Worlds final (14 Nov 2026 19:00:00Z), OPEN row P11

Posted 14 Nov 2026 02:41Z, ahead of the 06:00Z deadline. Every figure below was measured on Prime
between 02:20Z and 02:40Z on 14 Nov. Note the note's own report path is honoured: this file is filed
under the note's own filename.

## 1. PM trades — a trade recorder IS running

- Process: transient unit `thesports-pmtrades.service`, MainPID 2271688, `ActiveState=active`,
  started **2026-11-14 02:09:30Z**, RSS 32.6 MB, elapsed 30 min at 02:40Z. Command:
  `/usr/bin/python3 -I /root/pkarbs/live/thesports/pm_trades_capture.py /mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b --interval 30`.
- It was started by the guard cron, not by hand: `/var/log/thesports_capture_guard.log`
  `2026-11-14T02:09:30Z relaunched thesports-pmtrades ok`, then `tick rc=0` at 02:10/02:15/02:20/02:25/02:30/02:35Z.
- `live/thesports/capture.py` is untouched — it still has no trade reader; this is a second process.
- Endpoint data-api `/v2/trades` (v1 retired), UA `pkarbs-thesports-trades/1.0`, no credentials, no key
  anywhere in the script. Dedup: in-memory key set + `trades.watermark.json` (max exchange ts per
  condition, saved each cycle, applied only on the first cycle after a start).
- **Newest trade row UTC:** `trades.jsonl` last row **2026-11-14 02:39:33.228Z** (measured at 02:39:43Z);
  file 4,916,217 B. By sport, newest: tennis 02:34:11.142Z, nba 02:34:10.782Z, cs2 02:10:02.984Z.
- Revert: remove the two trade blocks from `guard_capture_b.sh`
  (backup `guard_capture_b.sh.bak-p11-20261114T020733Z`, byte-identical pre-edit copy),
  `kill 2271688`, `rm /root/pkarbs/live/thesports/pm_trades_capture.py`. `trades.jsonl` is kept.

## 2. Newest books row and newest trade row, per game

All times UTC, measured 02:35-02:40Z. Books rows are written only when a book's top-15 hash changes,
so a "newest books row" is the last *change*, not proof of an unchanged-but-polled book.

| game | market named | newest books row | newest trade row |
|---|---|---|---|
| CS2 | `cs2-revise-esb-2026-11-13` (Revise vs eSuba, child_moneyline, registered 13 Nov 18:16:51Z) | **2026-11-14 02:31:05.193Z** | **2026-11-14 02:10:02.984Z** on `cs2-bar2-chama-2026-11-13` (BARCA vs BORRACHEIROS, Map/moneyline, price 0.88, size 1.465908) |
| Dota 2 | `dota2-synaps-nh-2026-11-13` (Team Synapse vs No Hoodwink, moneyline, registered 13 Nov 18:16:52Z) | **2026-11-14 01:58:25.385Z** | **none — 0 Dota 2 rows have ever been written** |
| LoL | none live at measurement time | **none in the last 600,000 books rows** | **none — 0 LoL rows have ever been written** |

- Whole-file trade counts: tennis 2,726, nba 5,481, cs2 1,182, dota2 0, lol 0.
- Why Dota 2/LoL have no trade rows: `pm_trades_capture.py` polls only conditions whose event start is
  inside `--behind 6h .. --ahead 48h`. At 02:37Z `dota2-synaps-nh` (start 13 Nov 18:00Z) is 8.6 h old,
  so it is outside the window, and no Dota 2 market is inside it: a full-pagination gamma probe
  (tag `dota-2`, active, closed=false, end_date_min = now-1h) returned **0 markets in the capture's
  registration window at 02:37Z** (same probe for `counter-strike-2`: 0 in-window too; the CS2 rows above
  come from markets registered earlier and still being polled by `capture.py`'s token set of 344 tokens).
- Coverage of the final itself is not affected: when the final registers (item 3) its start is inside the
  +48 h ahead window, so the trade recorder picks it up on its next 30 s cycle.
- No live Dota 2 or LoL market exists right now to name: gamma shows the Worlds final as the only open
  LoL game event, starting 19:00Z.

## 3. LoL Worlds final markets — listed on Polymarket, NOT yet registered by us, first pickup 18:40-18:45Z

- **Not in `markets.jsonl`.** It holds 40 LoL rows in total; the newest LoL registration is
  **2026-11-12 05:41:15.495Z** (`lol-nh1-sgw-2026-11-12`, LCP Promotion Playoffs). No row for the final.
- **The market exists on Polymarket** (public gamma read at 02:33Z, using the capture's own query shape
  `tag_slug=league-of-legends, active=true, closed=false, end_date_min=now-3600`): event
  `lol-blg-gen-2026-11-14`, title `LoL: Bilibili Gaming vs Gen.G (BO5) - Worlds Playoffs`,
  startTime/gameStartTime **2026-11-14T19:00:00Z**, `closed=false`, **47 markets** including the
  `moneyline` match winner and `child_moneyline` `Game 1/2/3/4 Winner` — exactly the two
  `sportsMarketType`s `MKT_TYPES` accepts.
- **Why it is not registered yet:** `discover_pm()` skips a market unless
  `st - 1200 <= now <= st + 6h`, i.e. it can first be picked up **20 minutes before gameStartTime =
  18:40:00Z**. This is the existing gate in `capture.py`, not a fault; it was not changed here.
- **Pass cadence: every 300 s (5 min), requirement is at least every 10 min — met.** Measured from
  `log.jsonl` `discover_pm` rows: 01:59:05.884, 02:04:13.711, 02:09:20.956, 02:14:27.822,
  02:19:35.962, 02:24:43.009, 02:29:50.085, 02:34:56.653Z — 308 s apart, 1,377 rows in the file,
  `tokens` 344 (2 new at 02:14:27Z). `capture.py` has been up since **13 Nov 18:16:51Z** with
  `creds:true` and `lol` in its sports set.
- **Expected first registration: the first pass at or after 18:40:00Z, i.e. 18:40:00-18:45:00Z**
  (15-20 min before the 19:00:00Z start). Books then poll those tokens at 1 s (`--book-every 1.0`).
- If the reviewer wants books before 18:40Z, that is a one-constant change to the `1200` window gate in
  `capture.py` — a code change, NOT applied here, left to the reviewer.

## 4. Guard covers the trade file

- `live/thesports/guard_capture_b.sh` P11 addendum (backup `guard_capture_b.sh.bak-p11-20261114T020733Z`,
  `bash -n` OK, `GUARD_DRYRUN=1` run rc=0 at 02:37Z, live relaunch branch proven 02:09:30Z):
  - freshness set is now `for f in books pmws ts_mqtt log trades; do ... stat -c %Y ...`
    — the trade file is in the 600 s staleness rule;
  - `trades_check()` runs first every tick and relaunches `thesports-pmtrades` when the
    `pm_trades_capture.py` process is absent (read from `/proc/*/cmdline`, never `pgrep -f`).
- **Caveat, for the reviewer to rule on:** the age rule is *max across the set* — it restarts only when
  the **newest** of books/pmws/ts_mqtt/log/trades is older than 600 s. So a trades file that goes quiet
  while books/pmws stay fresh does not by itself restart anything; a dead recorder is caught by the
  process check instead. Making trades a per-file rule would restart `capture.py` on a legitimately
  quiet trades file, so it was not done. If per-file trades staleness is wanted, say so and it is a
  two-line change.

## 5. Disk — data disk only, no capture on root

- All three writers are on the data disk: `books.jsonl` 8,836,833,331 B, `ts_mqtt.jsonl` 9,233,878,550 B,
  `pmws.jsonl` 40,318,612 B, `trades.jsonl` 4,916,217 B — all under
  `/mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b/`, which is the process's own output path. `/vol2` is now a **symlink to
  that same data volume** (created 13 Nov 17:44Z), so it no longer resolves onto root.
- **Free space, `df -B1` at 02:39:43Z:** total 105,089,261,568 B, used 27,461,599,232 B,
  **free 72,242,176,000 B (67.3 GiB)**. Root (not used by these captures) 17,198,211,072 B free.
- **Measured growth, 75 s window 02:28:42 → 02:29:57Z:** books +1,775,019 B (**2.05 GB/day**),
  ts_mqtt +2,674,893 B (**3.08 GB/day**), trades +73,317 B, pmws +4,874 B (5.6 MB/day), markets unchanged.
  Trades measured again over 02:24 → 02:39Z: +770,759 B in ~15.7 min ≈ **71 MB/day** (windows gave
  49-84 MB/day; it is bursty).
- **Projection to 15 Nov 23:59Z (45.5 h):** ≈3.9 GB books + 5.9 GB ts_mqtt + 0.13 GB trades + 0.01 GB pmws
  ≈ **10 GB**, leaving **≈ 62 GB free** on the data disk. The `share/` gzip copies (2.2 GB: books 1.34 GB,
  ts_mqtt 0.92 GB) are replaced every 600 s, not accumulated.
- **Report-and-proceed:** the recorder's own gate note says "GO at 50 MB/day"; measured trades growth is
  71-84 MB/day now. Headroom is unaffected (≈0.13 GB through 15 Nov), so nothing was stopped — reviewer
  may re-set the figure.
- `goalserve` and `pandascore` still write to root; that is OPEN row P7 and is untouched by this reply.

## OPEN / NOT VERIFIED

- First registration of the final (due 18:40-18:45Z) and the first books/trade rows for it — cannot exist
  before then; not yet measured.
- Dota 2 and LoL trade coverage is unproven (0 rows each); no live market of either game existed at
  measurement time to prove it on.
- Per-file (rather than max-across-files) trades staleness in the guard — not implemented, awaiting the
  reviewer's ruling above.

Count: notes run 1, outstanding 0, PENDING open 0.
