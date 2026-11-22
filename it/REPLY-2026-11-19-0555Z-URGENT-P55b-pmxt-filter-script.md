# IT: P55b, committed and tested PMXT filter script (the "send a script" you asked for)

Goal: automated edges toward $500/day; here, the real best ask of the gas favourite at 02:45 and 03:00 ET, before the AAA release (about 03:15 ET).
Measured position: last-trade view only (top bucket above 0.50 at 03:00 ET on 93% of 28 days, wins 86%); real asks are unmeasured. Script merged on the default branch: PR #446, squash f5f7ca90 (scan/gas_window/pmxt_gas_filter.py and test_pmxt_gas_filter.py). SETTLED.md e2a25c41beffd3f4438590a691fc2ed07402838b.
Single most important item: Nick needs the asks now; run P55a (index curl) first, then this.

1. `python3 scan/gas_window/test_pmxt_gas_filter.py` must print `3 of 3 PASS` (needs `pip install pyarrow`).
2. P55a: paste the first 4000 bytes of the archive index and the file pattern. I will send the exact `--url` the same hour.
3. P55b command shape: `python3 scan/gas_window/pmxt_gas_filter.py --url '<pattern with {Y}{m}{d}{H}>' --days 2026-10-22:2026-11-19 --hours 6,7,8 --out /mnt/HC_Volume_107257520/gas_books_pmxt --min-free-gb 15`. It resolves the gas token ids from Gamma itself, deletes each download after filtering, stops under 15 GB free, logs MISSING for 404 hours. First run with `--list-only` and paste the URLs; then run it.
4. Paste stdout (one line per hour: OK/MISSING, rows read, rows kept). No header, proxy or user-agent changes.
