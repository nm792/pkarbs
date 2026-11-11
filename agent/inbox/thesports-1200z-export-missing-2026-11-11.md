# The 12:00Z TheSports 2h export has not landed (11 November 2026)

The last ts_mqtt/books_mid commit for final-topics-32295b-slim is b091e49bb at 09:59:17Z. Nothing has landed for the 12:00Z slot (it is now past 12:30Z). Tennis T1 is at 59 of 60 and needs only the next export to reach its target.

Please, in one reply in agent/outbox by 13:10Z:

1. Say why the 12:00Z export is missing (timer did not fire, build still running, push rejected non-fast-forward, shrink guard refused it, or other).
2. Run the export now, rebase and push if the push raced, and give the commit hash.
3. If the 5% shrink guard refused it, say which file and the sizes, and push the files that pass the guard instead of skipping the whole export.

The tennis target decides a pre-registered test, so this is priority 1 ahead of Netflix and the other recorders.
