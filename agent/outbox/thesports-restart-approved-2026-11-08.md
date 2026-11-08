# outbox: thesports-restart-approved-2026-11-08 — RAN

Nick's approval (2026-11-08 00:00:14Z "Yes", inbox thesports-restart-approved-2026-11-08) executed.

- Relaunch: live/thesports/capture.py via start_writer.sh — writer-starts.log shows `2026-11-08T00:11:22Z project=pkarbs mb_day=300 path=…/thesports/final-topics-32295b gate_rc=0 launch unit=thesports-capture-b rc=0`.
- Process: pid 2791157/2791163, started ~00:21Z into new chunk `final-topics-32295b` (spool /mnt/HC_Volume_107257520/pkarbs/thesports/). Single instance confirmed (one timeout+one python for the same chunk path).
- First fresh timestamps after restart: books.jsonl mtime 00:31Z (22,754 rows), pmws 333 rows, log counts line `{"ms":1794097883641,…,"books":22554,"pmws":329}` at ~00:31Z. Row counts 10 min later: books 22,754.
- Chunk tree: books.jsonl, markets.jsonl, pmws.jsonl, log.jsonl + `share/` gz copies (all fresh 00:31Z).
- The 11:02Z–16:00Z gap slim export and the standing 2h export cadence: to be handled in the follow-on export task (this reply confirms RAN per item 2). No orders, nothing deleted, no credentials in git.
