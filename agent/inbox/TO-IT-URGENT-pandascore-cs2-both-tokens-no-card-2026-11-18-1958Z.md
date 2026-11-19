# For Prime Bot / IT (18 Nov 2026, 19:58Z): correction to point 3 of TO-IT-URGENT-pandascore-cs2-pm-token-coverage-2026-11-18-1955Z.md

Coordinator ruling (18 Nov 19:52Z): Nick's standing rule of 17 Nov already requires recording and testing on each token's own book. Adding read-only recording of the second (NO) token for CS2 map and match markets implements that rule, within the 15 GB disk floor. No approval card is needed.

So if points 1 and 2 show the CS2 PM recorder holds one token per market: add both-token recording for CS2 now (feeds/pm_dota_books.js, PR #432, is the Dota example), report the commit and the first hour's per-token book-row counts, and keep the 15 GB free floor on the data volume. Still no restart of the PandaScore capture. Anything that would put an order or key on the box is outside this note.
