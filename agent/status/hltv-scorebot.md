# Status: hltv-scorebot — Run 1 PASS met; node DIED 13:36Z, RELAUNCHED 14:19Z

**State:** RELAUNCHED RUNNING — Run 1 launched 12:19Z (systemd-run, MemoryMax 400M, ends 16:00Z). Node received SIGTERM at 13:36:58Z (capture.log `SIGTERM ... done`); no process remained. Relaunched 14:19:46Z as transient unit `hltv-scorebot-run1.service` (pid 798702, MemoryMax 400M, same config-run1.json, same end 16:00Z). Heartbeat 2026-11-04T14:21Z.
**Raw output:** `/root/hltvcap/run1-2026-11-04/` — scorebot.jsonl (23,539+ rows, growing), books.jsonl, capture.log, http.jsonl, markets.jsonl, stdout.log. Copied to `live/cs2_feeds/raw/hltv-2026-11-04/` (commit e23bd2d, owner-thread branch 6tydow).
**Pass / fail (per task):**
- scorebot.jsonl has >=50 `"ev":"log"` rows with `"Kill"` for match 2400076 (MEIA NOITE vs DAMAJUANA, 13:00Z): **PASS MET** — 2,307 `ev:log` rows, 1,811 with `Kill`, captured live through the 13:00Z match window before the 13:36 death.
- books.jsonl rows for that match's slug: **present**.
- `timedatectl` NTP synchronized: **yes** (prior check).
- Match pages 403 (Cloudflare challenge on 2400076/2400004/2400005) — capture runs via the public scorebot fallback URL (`scorebot-lb.hltv.org`), which is delivering rows.
**Cause of 13:36 death:** not established — no OOM record for this node in dmesg (the 13:36 OOM kill was mm-poly-ws.service pid 2076221, unrelated). SIGTERM emission source unverified; node relaunched per the authorized Run 1 window (ends 16:00Z).
**Copy cadence:** run1 raw pushed at 14:21Z (this round). Next 30-min copy due ~14:45Z and at 16:00Z end.
**Errors:** none current. **waiting for Nick:** none — Run 1 was Nick-approved (4 Nov 11:31Z).
