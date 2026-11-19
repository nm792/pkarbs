# To IT: PandaScore post-restart readback (16 Nov 18:05Z), count only, due 20:00Z

The 12:28Z restart note (#339) says row-level readback was not verified. Hours 13:00Z to 17:00Z are now closed gzip files, so please read them back. One chunked task, read-only. Cite feeds/STANDARD-feed-latency-test.md; no lead or verdict.

1. Per closed hour since 12:25:21Z: status rows per match, and the number of distinct matches.
2. Close errors since restart by code (4004 expected 0; any other code, which match).
3. Receive gaps over 60 s since restart: count and max per match, and whether each gap lines up with a close error or reconnect (yes/no).
4. Sockets: how many tasks started and connected, and any task that ended early (reason).
5. If BLAST data exists by 20:00Z, a priced-event recount per title and volume stratum (<$25k, >=$25k): events with PM book rows within +/-60 s and distinct match counts, same format as recount-318-final.md.

If rows are missing or 4004 returned, say so first; that becomes urgent.
