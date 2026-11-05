# from_agent — cricket feeds capture started 5 Nov (TASK-cricket-feeds-2026-11-05)

## RESULT
1. **Capture RUNNING** — started 2026-11-05 01:51:47Z (before the 03:30Z first-match window). Unit cricket-feeds.service, MemoryMax 500M / SwapMax 0, timeout 58000 (~16 h to 17:15Z).
2. **Files growing** at 01:52Z: books.jsonl 72 rows, markets.jsonl 37, espn_hdr.jsonl 1, log.jsonl 2. books+espn grow through WBBL Strikers v Heat (04:40-08:00Z) as required.
3. **Command used** (per task; --scope dropped for a detached transient unit so it survives idle restarts):
   cd /root/cricket-feeds && systemd-run --unit=cricket-feeds -p MemoryMax=500M -p MemorySwapMax=0 timeout 58000 python3 /root/cricket-feeds/capture.py /root/cricket-feeds/2026-11-05 15.9 --share /root/cricket-feeds/2026-11-05/share
4. No P&L, no orders. Read-only HTTP + one WS.

## DATA
- raw: /root/cricket-feeds/2026-11-05/{books,markets,espn,log}.jsonl; share copy committed hourly to rn1/scores/cricket/feeds-2026-11-05/.

## OPEN / NOT VERIFIED
- +15 min check (books growing into WBBL) — confirmed next status update.

## Count
notes run 1 (cricket-feeds started); PENDING open 0.
