# P122a RE-RUN with fixed pre-flight, then P122b (Nick approved 13:53Z, still in force)

Your 16:25Z FAIL (3 of 12 lacking rows) was a fault in MY pre-flight, not the recorder: resolved markets have no order book (CLOB /book = 404) and can never produce rows. Fixed in PR 471, default tip e309b08f75. I ran it against live Polymarket: PASS (11 in-window markets with a book, 1 resolved excluded, 395 rows).

1. Fresh clean export of default branch at e309b08f75 or later. Re-run P122a exactly as before (TMPDIR on the volume). Expect exit 0.
2. Exit 0 -> run P122b now (restart onto this export with the exact old command line, keep pm_dota_books.js.old, keep all files). Exit 1 -> do not restart; post the full output.
3. Within 15 minutes post the HEALTH READ: tokens line "discovery markets N tokens 2N", one node pid, books.jsonl growth at two reads 60 s apart, df.
Do not edit any script.
