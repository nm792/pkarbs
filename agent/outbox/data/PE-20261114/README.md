# TheSports/Polymarket cricket overlap count — evidence index

Count-only, read from Prime data-volume sources on 14 Nov 2026. This directory contains the selected-market/token rows, fixture aggregates, and TheSports match aggregates. No price join or latency evaluation was performed.

- `markets.csv`: 40 market records, 80 outcome tokens; registration window 10 Nov 04:00Z through 12 Nov 12:34Z.
- `markets_by_fixture.csv`: 32 distinct fixture slugs/titles; 19 fixtures have matched Polymarket book rows in the book window.
- `matches.csv`: legacy intermediate; retained only as an audit of token-level counts.
- `ts_matches.csv`: 30 TheSports match IDs and event-candidate counts.

Event candidates are distinct (match, inning, team_id, over, ball) keys with runs 4 or 6, nonzero wicket flag, or ball number 6. Categories overlap; union is counted once. The payload has numeric team IDs, not names; no name crosswalk was present in the captured data. The cricket market fixtures therefore cannot be reliably paired by team names to TheSports match IDs from this dataset alone.
