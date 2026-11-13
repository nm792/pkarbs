# Reply: Polymarket recorders for the CS2/Dota/TheSports matches - measured 16:22-16:29Z (13 Nov)

Answers `agent/inbox/TO-IT-URGENT-polymarket-recorders-dead-2026-11-13-1615Z.md`.
Read-only measurement; nothing was restarted, because no stream in this note is dead.
All times UTC, taken from the newest row of each file (not from process state).

## 1. Which process records what

One process records all four TheSports-side streams:
`python3 -I <repo>/live/thesports/capture.py <data-vol>/final-topics-32295b 160
--share <data-vol>/final-topics-32295b/share`, unit **thesports-capture-b**, pid 2818605,
up 5 d 15 h (started 8 Nov); threads: mqtt, poll, pmws, books, share.

| stream | file | newest row (measured) | state |
|---|---|---|---|
| PM market registration | `markets.jsonl` | **12 Nov 12:13:43Z** | **STOPPED** - gamma `/events` page cap |
| CLOB books, 1 s | `books.jsonl` | **13 Nov 16:25:49Z** | LIVE (8,481,109 rows at 16:22Z counts) |
| PM sports WS rows | `pmws.jsonl` | **13 Nov 16:25:40Z** | LIVE (live `dota2` rows in the same second) |
| TheSports MQTT | `ts_mqtt.jsonl` | **13 Nov 16:25:18Z** | LIVE (topic `thesports/csgo/match/v1`) |

Counts line in `log.jsonl` at 16:22:57Z: markets 2,847, ts_mqtt 5,197,980, books
8,481,109, pmws 182,072 - every counter rising except `markets`.

## 2. Why registration is stopped, and why no restart was done

`discover_pm` has returned HTTP 406 on every call since 12 Nov 12:39Z. Bisected against
the exact endpoint: `limit<=50 -> 200`, `limit>=51 -> 406`; the capture sends
`limit=100`. The fix is a code edit (limit 100 -> 50 plus page stride) filed as
**class-4 approval #21** in `dialogue/APPROVALS.md`. **A restart alone does not fix it**
and would only add a gap, so nothing was restarted.

## 3. The "trades stopped 12 Nov 05:36Z" line in the note

That figure is the **repo export slice** `rn1/scores/thesports/final-topics-32295b-slim/pmws.jsonl.gz`
(mtime 13 Nov 07:19Z, newest row 12 Nov 05:36Z), not a recorder: the exporter copies
`pmws.jsonl` and **deletes the copy when it exceeds 950,000 B**, so the slice stopped
being replaced once the file outgrew the pre-push hook. The live file on the data volume
is current to 16:25:40Z. Same diagnosis as `agent/outbox/thesports-pm-recorder-stale-2026-11-13.md`
(16:14Z).

**Separately, this capture records no Polymarket trade stream at all** - `capture.py`
has no trade reader (its file list: ts_mqtt, ts_poll, books, markets, pmws, log) and a
census of the last 1 MB of both `books.jsonl` and `pmws.jsonl` found 0 trade-shaped rows
(every `books` row is `{asks,bids,ms,sent,tk,ts}`). The only CLOB trade recorder on this
box is the MFW `rec_clob_trades.py`, which covers BTC up/down 5 m markets only, not
esports. So for these CS2 and Dota matches there is **no PM trade stream that could be
stale**; adding one would be a new collector (class 4).

## 4. Binding to the live matches (the note's item 3)

- `pmws.jsonl` already carries the live Dota rows this note cares about, e.g.
  16:25:40Z `dota2` "angry birds vs Team Synapse" and "4ikibamboni vs Spirit Academy",
  both `live:true, status:running`.
- `books.jsonl` rows are token-keyed, not match-keyed, so pairing needs
  `markets.jsonl`, which is frozen at 12 Nov 12:13:43Z with 2,847 registered tokens.
  Matches registered on or before that time can be paired from data already on disk
  (method in the 16:14Z reply); **games registered after it need approval #21 applied
  first** - that is the blocker, not a dead process.

## 5. What blocks what (the note's item 5)

- Registration frozen -> approval #21 (code edit + restart of the same unit).
- Writes go to `/vol2`, which resolves to the root volume -> approval #20 (repoint
  `PAYDIR`/`OUT` to the data volume, move, restart, delete the root copies only after
  row counts match). Root free was 17.47 GB at 16:2xZ, above the 15 GB floor, and the
  payload store self-stops at the floor either way.
- No esports PM trade stream exists anywhere on this box -> new collector, class 4,
  not raised by this reply.

Nick has not been asked for anything by this reply; #20 and #21 are already filed for
the daily approval batch.
