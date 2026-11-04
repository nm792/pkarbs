# Status: hltv-scorebot — Run 1 PASS met; node DIED 13:36Z, RELAUNCHED 14:19Z

**State:** RELAUNCHED RUNNING — pid 798702, MemoryMax 400M, ends 16:00Z. Heartbeat 2026-11-04T15:08Z.
**Pass met:** >=50 `"ev":"log"` Kill rows for match 2400076 (13:00Z) — captured live before the 13:36 death. scorebot.jsonl now 762 MB (15:08Z), still growing.
**Raw copy 15:08Z:** gzip of scorebot/books/capture/http/markets/stdout to `live/cs2_feeds/raw/hltv-2026-11-04/` on thread 6tydow (commit bc087169, overwrite per task spec, scorebot.gz 52 MB).
**Next:** 30-min copy at ~15:45Z and cleanup at 16:00Z end.
**Cause of 13:36 death:** not established (no OOM for this node in dmesg; SIGTERM source unverified). Node relaunched per authorized Run 1 window.
**Copy cadence:** next 30-min copy ~15:45Z, final + cleanup at 16:00Z.
**Errors:** none. **waiting for Nick:** none — Run 1 Nick-approved 4 Nov 11:31Z.
