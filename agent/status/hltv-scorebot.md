# Status: hltv-scorebot — Run 1 PASS met; node RUNNING, 30-min copy 14:49Z

**State:** RUNNING — Run 1 launched 12:19Z (systemd-run, MemoryMax 400M, ends 16:00Z). Node died 13:36:58Z (SIGTERM), relaunched 14:19:46Z as transient unit `hltv-scorebot-run1.service` (pid 798702, MemoryMax 400M, same config-run1.json, same end 16:00Z). Heartbeat 2026-11-04T14:49Z. Raw ps (14:49Z): `798702 29:0x node capture.js config-run1.json /root/hltvcap/run1-2026-11-04 2026-11-04T14:19:46Z 2026-11-04T16:00:00Z`.
**Raw output:** `/root/hltvcap/run1-2026-11-04/` — scorebot.jsonl (725 MB at 14:48Z, growing), books.jsonl, capture.log, http.jsonl, markets.jsonl, stdout.log.
**Pass / fail (per task):** scorebot.jsonl has >=50 `"ev":"log"` rows with `"Kill"` for match 2400076 (MEIA NOITE vs DAMAJUANA, 13:00Z): **PASS MET** (2,307 ev:log rows, 1,811 Kill) captured through the 13:00Z window before the 13:36 death. books.jsonl rows present for that match. NTP sync yes. Match pages 403 (Cloudflare) — capture runs via public scorebot-lb.hltv.org fallback, delivering rows.
**Copies:** 14:21Z (e23bd2d) + **14:49Z (727c63e4, this round)** raw gz → `live/cs2_feeds/raw/hltv-2026-11-04/` on thread 6tydow. Next 30-min copy ~15:15Z, final at 16:00Z end.
**Cause of 13:36 death:** not established — no OOM for this node in dmesg (13:36 OOM was mm-poly-ws pid 2076221, unrelated). Relaunched per the authorized Run 1 window.
**Errors:** none current. **waiting for Nick:** none — Run 1 was Nick-approved (4 Nov 11:31Z).
