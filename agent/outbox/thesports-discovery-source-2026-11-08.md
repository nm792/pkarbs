# Reply — thesports-discovery-source (2026-11-08)

Round 2026-11-08T13:1xZ. Read-only, from live spool `/root`-bank pkarbs thesports spool. No code change.

RESULT:
- The "no market rows" premise came from the 02:01Z-clipped slim export, not the spool. The LIVE spool markets.jsonl (760 rows, last ms 1794143584948 = 13:13:04Z) HAS 6 of the 7 listed slugs, all discovered by `discover_pm()` and with live book rows via their clobTokenIds (56,319 book-row matches for those 12 tokens in books.jsonl): wta-liu-eala-2026-11-08 (07:44Z), atp-staehel-tange-2026-11-07 (03:02Z), atp-langmo-vujic-2026-11-07 (03:12Z), atp-imai-kouzmin-2026-11-07 (03:02Z), atp-saitoh-takahas-2026-11-07 (03:02Z), atp-watanuk-kumstat-2026-11-08 (06:12Z).
- The one genuinely absent slug, atp-wong-watanuk-2026-11-07: no market row and no title match (no "Wong vs Watanuki" title) in the spool. Cause: it is a 2026-11-07 match; the capture booted 00:11Z on 11-08 and `discover_pm`'s gameStartTime filter keeps only [start−20 min, start+6 h] — by boot the window had already closed, so it was never discovered. An 11-08 rerun outside that window cannot recover it; recovery would need a one-off fetch bounded outside the window (proposed, not applied).
- Row counts: live spool markets.jsonl = 760 rows, log.jsonl = 244 rows; committed slim exports on origin are the clipped (02:01Z/02:16Z) set, so they do not show these rows.

DATA: spool `/pkarbs/thesports/final-topics-32295b/{markets,log,books}.jsonl` (no IPs written).

OPEN / NOT VERIFIED:
- Full-file re-export of spool markets.jsonl (→ 760 rows vs clipped 358) + log.jsonl to the slim path would make origin match the live spool; left for the next guard-timer run unless a re-export is wanted now (state in reply).

Count: notes run 1, outstanding 0, PENDING open 0.
