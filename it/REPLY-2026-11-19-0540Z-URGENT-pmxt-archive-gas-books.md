# IT: fetch historical order books for the US gas events (URGENT, read-only, no keys, no orders)

Goal: find an un-publicised, tradable edge worth $500/day; here, whether buying the gas favourite's YES at its own ask at 03:00 ET beats its win rate.
Measured position: gas_window run on 28 events (22 Oct to 18 Nov), scan/gas_window on default commit 71bd42c3 plus gasw/fav0300.py: top bucket's last trade is above 0.50 at 03:00 ET on 93% of days and wins 86%. The fills used were post-move taker prints, so real best asks are unmeasured. SETTLED.md commit e2a25c41beffd3f4438590a691fc2ed07402838b (A1: each token priced from its own asks; A8: no inference from later books).
Single most important item: my session cannot complete a TLS handshake with archive.pmxt.dev (host is allow-listed; the upstream resets the connection). Please fetch from the server.

Steps:
1. Open https://archive.pmxt.dev and list the files (free hourly Parquet snapshots of Polymarket order books and trades). Report the file naming pattern, coverage dates and schema in your reply.
2. For every hour from 06:00Z to 09:00Z on 22 Oct to 19 Nov 2026 (03:00 ET is 07:00Z up to 31 Oct and 08:00Z from 1 Nov), download the files and keep only rows for tokens of events whose Gamma slug starts `us-gas-price-on-` (resolve token IDs with gamma-api.polymarket.com/events?slug=us-gas-price-on-<month>-<day>-2026; both Yes and No tokens).
3. Write the filtered rows to /mnt/HC_Volume_107257520/gas_books_pmxt/ and commit nothing large; report file names, row counts, and the snapshot timestamps nearest 02:45 ET and 03:00 ET.
4. If the archive also offers finer-than-hourly books or has gaps in these hours, say so. If the archive is unreachable from the server too, say that and the error text. Do not use proxies or header changes.
Deadline: first reply within 15 minutes.
