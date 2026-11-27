# IT row P147: read-only report on the P121 will-say paper logger (mentions) + earnings-beat books
Order: Nick 26 Nov 04:08Z via coordinator. Paper only, public Gamma reads, no orders, no keys. Offline script, no server code, no restart.
Why IT: the P121 output folder (decisions.jsonl, fills.jsonl, earnings_beat/books.jsonl) lives only on Prime; no cloud copy exists, so the first number cannot be produced anywhere else.

## Pre-flight (light gate: load1<12, MemAvailable>=2000 MB, MemoryMax 1G, CPUWeight 20, nice 19, ionice -c3, timeout 900)
```
cd <pkarbs checkout>/it
python3 -I test_mentions_p121_report.py     # expect 15 of 15 pass
python3 -I test_mentions_beat_forward_list.py   # expect 4 of 4 pass
```
Any failure = nothing runs, paste the failure.

## Run (read-only; writes one text file)
```
python3 -I mentions_p121_report.py --scorer mentions_pm_daily_scorer.py \
  --state /mnt/HC_Volume_107257520/pkarbs/mentions/daily/state \
  --out   /mnt/HC_Volume_107257520/pkarbs/mentions/ws-paper --cap 200
```
(If the P121 folder is elsewhere, use the --out the supervisor uses; the file decisions.jsonl must be in it.)
Expected write: one REPORT-<date>.txt, a few KB, in <out>/reports/. Also print `wc -l decisions.jsonl fills.jsonl earnings_beat/books.jsonl` and `cat heartbeat.json`.

## Paste back (commit or paste into this thread's INBOX answer)
1. The full REPORT text, in particular the line starting "FIRST NUMBER:" and the line "sanity: recomputed off-key fair equals the logged fair on N of M".
2. heartbeat.json (ts, universe_failures) so the 15-minute health read (R-037) is on record.
Daily from then on: same command, one row per day, same light gate. Beat list live version (reads Gamma + CLOB, no Prime files): `python3 -I mentions_beat_forward_list.py` (appends beat_forward_<date>.csv).

## Known limits (stated, not hidden)
- Takes are the logger's own-token ladder at decision time, so sizes are MEASURED depth; the number is FLOOR/UNPROVEN until >= 100 resolved takes.
- KEEP_THRESHOLD on is a re-pricing of logged takes. Tokens the on key would take that cleared 10c only under on are not observable (P121 logs only off-key candidates): reported as on_only_more, never invented. Logging both keys would be a logger change (server code, restart): NOT requested here.
