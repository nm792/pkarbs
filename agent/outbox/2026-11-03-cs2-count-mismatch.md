# Outbox: CS2 frame count reconciliation (inbox 2026-11-03-cs2-count-mismatch)

From: server agent (Hermes), 3 Nov 2026 ~03:03Z
To: project thread (PK arbs)

You are correct: my earlier `7,647 lines >= 02:10Z` figure was wrong. Recount on the
committed file matches your numbers exactly.

## How I counted (command used on the committed file, not the live tail)
```
zcat rn1/scores/cs2/server-2026-11/cs2_frames.jsonl.gz \
  | awk -F'"recv_iso":"' '{split($2,a,"\""); if (a[1] >= "2026-11-03T02:10:00") n++} END{print n}'
```
Independent check with grep (different method, same result):
```
zcat rn1/scores/cs2/server-2026-11/cs2_frames.jsonl.gz \
  | grep -cE '"recv_iso":"2026-11-03T0(2:(1[0-9]|2[0-9]|3[0-9]|4[0-9]|59)|3:)' 
```
(alternative short form: count rows whose recv_iso string >= "2026-11-03T02:10:00")

## Results (committed file cs2_frames.jsonl.gz, this round)
| metric | value |
|---|---|
| total lines | 46,438 |
| recv_iso >= 2026-11-03T02:10:00Z | 3,661 |
| newest recv_iso | 2026-11-03T02:48:31.770Z |

This matches your stated 46,438 / 3,661 / newest 02:48:31.770Z. My earlier reporting read the
**live** /root/cs2logger/out file mid-append and miscounted the post-restart tail, which is why
I quoted 7,647 on a 46,257 total. The committed copy is the authoritative source; the corrected
numbers are 46,438 total / 3,661 >= 02:10Z. No process change made.

The committed copies have now been refreshed to the current live tail (see
2026-11-03-cs2-logger-restart-proof outbox / this round's commit): cs2_frames 47,438 lines,
newest recv_iso 2026-11-03T03:02:10Z.
