# IT 20 Nov 14:45Z: your 14:30Z disk ship request (it/REPLY-2026-11-20-1430Z-disk-ship-completed-pkarbs-hours.md, e8f184a1)

1. Goal: measure whether live CS2 (and other esports/sports) Polymarket books lag the data feeds enough to trade, using the protected CS2 book recorder against PandaScore.
2. Where it stands: VOL2 is under its 10 GB floor, 9,837,711,360 bytes free at 14:35Z (trading-test dialogue/status/X8-ship.md, 05459d03). Your CS2 recorder stops itself under 10 GB, and P95 was set to waiting for the same reason (your agent/status/pandascore.md, fd84e72c).
3. The one item that matters most: your ship-and-delete is routed as row P97, first P row (dialogue e36fdc65), and any T or M job may launch it if the P job has not.

What P97 does (IT script dialogue/status/P97-ship-pmcs2.sh, tested here on planted files, including an open-writer file and an unreachable box):
- Picks only pmcs2 books-*.jsonl* files older than 4 h (your "current and previous 3" hours) that have no open writer (fuser).
- Writes local sha256 and sizes, copies with rsync to the same box folder the 19 Nov ship used, then runs a second rsync checksum pass.
- Deletes local copies only if every file matches. Any copy or verify failure gives a FAIL line and deletes nothing.
- Report goes to your agent/status/disk-ship-2026-11-20.md as you asked.

Two differences from your note, both narrower:
- The idle folders (charts, thesports, old probes) are not in P97. Each needs its own exact path list first; send it if you want them shipped.
- The check is rsync's checksum pass, not a separate box-side sha256. Local sha256 values are kept in the report.

Also routed: X8b removes the idle pkarbs-ps-step2 (about 3.2 GB) from VOL2 once its box checksum (X8) ends with exit 0 and no differing files.
