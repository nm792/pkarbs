# 12-month macro release pickoff scan (26 Oct 2026)

Run in a sandbox that can reach gamma-api and data-api.polymarket.com (this repo's container cannot).
Send a `User-Agent` header: data-api answers 403 to Python's default one.

1. `fetch.py` – finds closed US CPI / core CPI / jobs / unemployment / FOMC / PPI events whose first market
   closed 20 Oct 2025 – 26 Oct 2026, writes `/tmp/macro/meta.json`. Then drop non-US and odd events
   (`-uk`, `-eu-`, `fed-decision-in-september-568`).
2. `trades.py` – pages data-api `/trades?market=...` (newest first, 500 a page) back to 2 days before the
   first close. data-api refuses offsets above 10,000, so big FOMC events stop at 10,500 rows.
3. `capped.py 10` – re-pulls capped events one market at a time, trades of $10 or more only.
4. `fix1.py` – Nov 2025 monthly CPI closed a month after its release; re-pulls it back to the release.
5. `analyse.py` – release second, pickoff edge by seconds after release, release-day table (`days.json`).
6. `detail.py` – per-second profile and the large fills for a few release days.

Results: `days.json` (per release day) and `event-level.txt` (per event).
