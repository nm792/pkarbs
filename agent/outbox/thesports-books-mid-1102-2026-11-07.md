# Outbox: books_mid committed for slim-1102-32295 (7 Nov 2026, 13:0xZ)

Reply to `agent/inbox/thesports-books-mid-1102-2026-11-07.md`.

books_mid committed to `rn1/scores/thesports/slim-1102-32295/books_mid/` on branch claude/project-thread-vg2ckg (commit d7503e0).

- Coverage: chunk 32295 from 04:00Z onward — 10 hour dirs, 04:00Z..12:00Z complete + partial 13:00Z hour. 37 gz parts, 800,150 rows, max part 463 KB (all under the 5 MB hook). Row layout identical to the 8917 slim: {ms, tk, bb, ba, q} (q = bid size at mid*0.975 floored to 0.01).
- Source: live raw `/vol .../final-topics-32295/books.jsonl` (midpoint of best bid/ask, one row per token per second, deduped on ms).
- Partial hour naming matches 8917: incomplete current hour stored as `<hour_ms>.jsonl.gz` loose file, complete hours as `<hour_ms>/<bucket_sec>.jsonl.gz` per 900s.
- Note item 2 (books_mid in every later 2h export) and item 3 (outbox note): covered here; I'll keep books_mid in subsequent 2h slim exports.
- Nothing deleted or overwritten; raw books.jsonl untouched (still live, /vol).
