# SCHEDULE: decision-time book recorder for late-resolving series (R-036), dated 2026-11-22

Source: gamma `events/keyset?closed=false` read 22 Nov ~06:20Z for the 34 series in `it/resolving_books_series.txt` (`pipeline/out/listing1/resolving_books_snap_2026-11-22.json`). The recorder re-reads the open-event list every 10 minutes, so events listed later (the next day's Up/Down contracts, new Elon brackets) are picked up without any edit. A snapshot is taken at T-3 h, T-1 h and T-30 min (within +-60 s) of each event end, all candidate tokens in one POST /books.
Plausibility check (15 min after the first window): the first line of `resolving_books_YYYYMMDD.jsonl` must have `hours_to_end` within 0.02 of 3.0, a numeric `ask` between 0.01 and 0.99, and `latency_s` under 5.

Windows already known (events open on 22 Nov 06:20Z). Today's earliest: box-office-openings Sun 22 Nov 09:00Z (T-3h) and 11:00Z (T-1h); if the service is not up by 09:00Z the 09:00Z window is missed and the 11:00Z / 11:30Z windows still count.

| series | open events with this end | event end (UTC) | T-3h | T-1h | T-30m |
|---|---|---|---|---|---|
| box-office-openings | 7 | 2026-11-22T12:00:00Z | Sun 22 Nov 09:00Z | Sun 22 Nov 11:00Z | Sun 22 Nov 11:30Z |
| us-gas-price-daily | 1 | 2026-11-22T15:00:00Z | Sun 22 Nov 12:00Z | Sun 22 Nov 14:00Z | Sun 22 Nov 14:30Z |
| rotten-tomatoes | 2 | 2026-11-23T15:00:00Z | Mon 23 Nov 12:00Z | Mon 23 Nov 14:00Z | Mon 23 Nov 14:30Z |
| elon-tweets-48h | 1 | 2026-11-23T17:00:00Z | Mon 23 Nov 14:00Z | Mon 23 Nov 16:00Z | Mon 23 Nov 16:30Z |
| amzn-multi-strikes-weekly | 1 | 2026-11-23T21:00:00Z | Mon 23 Nov 18:00Z | Mon 23 Nov 20:00Z | Mon 23 Nov 20:30Z |
| tsla-multi-strikes-weekly | 1 | 2026-11-23T21:00:00Z | Mon 23 Nov 18:00Z | Mon 23 Nov 20:00Z | Mon 23 Nov 20:30Z |
| spy-daily-up-or-down | 1 | 2026-11-23T21:00:00Z | Mon 23 Nov 18:00Z | Mon 23 Nov 20:00Z | Mon 23 Nov 20:30Z |
| spy-daily-close-uo | 1 | 2026-11-23T21:00:00Z | Mon 23 Nov 18:00Z | Mon 23 Nov 20:00Z | Mon 23 Nov 20:30Z |
| spx-open-daily-up-or-down | 1 | 2026-11-23T21:00:00Z | Mon 23 Nov 18:00Z | Mon 23 Nov 20:00Z | Mon 23 Nov 20:30Z |
| spx-daily-up-or-down | 1 | 2026-11-23T21:00:00Z | Mon 23 Nov 18:00Z | Mon 23 Nov 20:00Z | Mon 23 Nov 20:30Z |
| russell-2000-daily-up-or-down | 1 | 2026-11-23T21:00:00Z | Mon 23 Nov 18:00Z | Mon 23 Nov 20:00Z | Mon 23 Nov 20:30Z |
| nvda-daily-up-down | 1 | 2026-11-23T21:00:00Z | Mon 23 Nov 18:00Z | Mon 23 Nov 20:00Z | Mon 23 Nov 20:30Z |
| msft-multi-strikes-weekly | 1 | 2026-11-23T21:00:00Z | Mon 23 Nov 18:00Z | Mon 23 Nov 20:00Z | Mon 23 Nov 20:30Z |
| meta-multi-strikes-daily | 1 | 2026-11-23T21:00:00Z | Mon 23 Nov 18:00Z | Mon 23 Nov 20:00Z | Mon 23 Nov 20:30Z |
| meta-daily-up-down | 1 | 2026-11-23T21:00:00Z | Mon 23 Nov 18:00Z | Mon 23 Nov 20:00Z | Mon 23 Nov 20:30Z |
| nvda-multi-strikes-weekly | 1 | 2026-11-23T21:00:00Z | Mon 23 Nov 18:00Z | Mon 23 Nov 20:00Z | Mon 23 Nov 20:30Z |
| googl-multi-strikes-weekly | 1 | 2026-11-23T21:00:00Z | Mon 23 Nov 18:00Z | Mon 23 Nov 20:00Z | Mon 23 Nov 20:30Z |
| gold-daily-up-or-down | 1 | 2026-11-23T22:00:00Z | Mon 23 Nov 19:00Z | Mon 23 Nov 21:00Z | Mon 23 Nov 21:30Z |
| silver-daily-up-or-down | 1 | 2026-11-23T22:00:00Z | Mon 23 Nov 19:00Z | Mon 23 Nov 21:00Z | Mon 23 Nov 21:30Z |
| khamenei-daily-tweets | 1 | 2026-11-24T17:00:00Z | Tue 24 Nov 14:00Z | Tue 24 Nov 16:00Z | Tue 24 Nov 16:30Z |
| trump-truth-social | 1 | 2026-11-24T17:00:00Z | Tue 24 Nov 14:00Z | Tue 24 Nov 16:00Z | Tue 24 Nov 16:30Z |
| ted-cruz-daily-tweets | 1 | 2026-11-24T17:00:00Z | Tue 24 Nov 14:00Z | Tue 24 Nov 16:00Z | Tue 24 Nov 16:30Z |
| cz-tweets | 1 | 2026-11-24T17:00:00Z | Tue 24 Nov 14:00Z | Tue 24 Nov 16:00Z | Tue 24 Nov 16:30Z |
| elon-tweets | 1 | 2026-11-24T17:00:00Z | Tue 24 Nov 14:00Z | Tue 24 Nov 16:00Z | Tue 24 Nov 16:30Z |
| zelenskyy-tweets | 1 | 2026-11-24T17:00:00Z | Tue 24 Nov 14:00Z | Tue 24 Nov 16:00Z | Tue 24 Nov 16:30Z |
| nycmayor-tweets | 1 | 2026-11-24T17:00:00Z | Tue 24 Nov 14:00Z | Tue 24 Nov 16:00Z | Tue 24 Nov 16:30Z |
| openrouter-ai-market-share | 3 | 2026-11-24T17:00:00Z | Tue 24 Nov 14:00Z | Tue 24 Nov 16:00Z | Tue 24 Nov 16:30Z |
| whitehouse-daily-tweets | 1 | 2026-11-24T17:00:00Z | Tue 24 Nov 14:00Z | Tue 24 Nov 16:00Z | Tue 24 Nov 16:30Z |
| earnings-call-mentions | 1 | 2026-11-25T04:59:00Z | Wed 25 Nov 01:59Z | Wed 25 Nov 03:59Z | Wed 25 Nov 04:29Z |
| elon-tweets-48h | 1 | 2026-11-25T17:00:00Z | Wed 25 Nov 14:00Z | Wed 25 Nov 16:00Z | Wed 25 Nov 16:30Z |
| earnings-call-mentions | 1 | 2026-11-26T04:59:00Z | Thu 26 Nov 01:59Z | Thu 26 Nov 03:59Z | Thu 26 Nov 04:29Z |
| elon-tweets | 1 | 2026-11-27T17:00:00Z | Fri 27 Nov 14:00Z | Fri 27 Nov 16:00Z | Fri 27 Nov 16:30Z |
| trump-truth-social | 1 | 2026-11-27T17:00:00Z | Fri 27 Nov 14:00Z | Fri 27 Nov 16:00Z | Fri 27 Nov 16:30Z |
| box-office-openings | 3 | 2026-11-29T12:00:00Z | Sun 29 Nov 09:00Z | Sun 29 Nov 11:00Z | Sun 29 Nov 11:30Z |
| rotten-tomatoes | 4 | 2026-11-30T15:00:00Z | Mon 30 Nov 12:00Z | Mon 30 Nov 14:00Z | Mon 30 Nov 14:30Z |
| elon-tweets | 1 | 2026-12-01T17:00:00Z | Tue 01 Dec 14:00Z | Tue 01 Dec 16:00Z | Tue 01 Dec 16:30Z |
| trump-truth-social | 1 | 2026-12-01T17:00:00Z | Tue 01 Dec 14:00Z | Tue 01 Dec 16:00Z | Tue 01 Dec 16:30Z |
| earnings-call-mentions | 1 | 2026-12-03T04:59:00Z | Thu 03 Dec 01:59Z | Thu 03 Dec 03:59Z | Thu 03 Dec 04:29Z |
| rotten-tomatoes | 1 | 2026-12-07T15:00:00Z | Mon 07 Dec 12:00Z | Mon 07 Dec 14:00Z | Mon 07 Dec 14:30Z |
| box-office-openings | 2 | 2026-12-20T12:00:00Z | Sun 20 Dec 09:00Z | Sun 20 Dec 11:00Z | Sun 20 Dec 11:30Z |
| box-office-openings | 1 | 2026-12-21T00:00:00Z | Sun 20 Dec 21:00Z | Sun 20 Dec 23:00Z | Sun 20 Dec 23:30Z |
| rotten-tomatoes | 2 | 2026-12-21T15:00:00Z | Mon 21 Dec 12:00Z | Mon 21 Dec 14:00Z | Mon 21 Dec 14:30Z |
| rotten-tomatoes | 2 | 2026-12-21T23:59:00Z | Mon 21 Dec 20:59Z | Mon 21 Dec 22:59Z | Mon 21 Dec 23:29Z |
| rotten-tomatoes | 2 | 2026-12-28T15:00:00Z | Mon 28 Dec 12:00Z | Mon 28 Dec 14:00Z | Mon 28 Dec 14:30Z |
