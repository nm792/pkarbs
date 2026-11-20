# ASSUMPTIONS: gas window, 20 Nov 2026 (every input marked MEASURED / PUBLISHED / ASSUMED; no run uses an ASSUMED input)

| Input | Status | Source |
|---|---|---|
| Taker fee formula and 0.04 Finance coefficient for the gas market; makers pay nothing | PUBLISHED + MEASURED | docs.polymarket.com/trading/fees.md; Gamma market field feeSchedule (ev20.json) |
| Fee change 20 Nov 23:59 UTC (Finance 0.05; tiered maker rebates) | PUBLISHED | docs.polymarket.com/programs/fee-and-rebate-changes-november-2026.md |
| Maker rebate for the gas market 25% of fees (current pool rule) | PUBLISHED | fees.md; feeSchedule.rebateRate 0.25 |
| Tick 0.001, min order 5 shares | MEASURED (Gamma market fields) | ev20.json |
| Market created 10:00:11 ET, trading start 15:00:26Z; Gamma shows it about 51 s after creation | MEASURED (one event) | books20/listing.json |
| First price needs a Yes bid and No bid that sum to 1 | PUBLISHED | concepts/prices-orderbook.md |
| Books empty (0.99 ask/0.01 bid placeholder) for ~7 minutes after listing | MEASURED (one event, 20 Nov) | books20 file |
| First fill 8 minutes after listing; bursts at +25 and +36 minutes | MEASURED (one event) | trades20_all.json |
| CLOB prices-history is a displayed price (midpoint, or last trade if spread > 0.10), not a trade or an ask | PUBLISHED | prices-orderbook.md |
| AAA page updates about 03:15 ET | ASSUMED (Nick); measurement pending | aaa_watch.py run launched 05:45Z, result not yet read |
| 10:00 ET reading of the AAA print is public at listing | PUBLISHED (rules) / ASSUMED for the first minutes | Gamma rules |
| Queue priority is price-time | ASSUMED | not in pages read |
| Latency send -> CLOB, 250 ms hold, ws broadcast, chain settle | ASSUMED / UNSOURCED | not read |
| Nowcast v0 (ridge, spot_lag 2) estimate and sd | MEASURED model, exploratory | scan/gas_window/nowcast.py 4001a87f; ties the market top bucket at +10 min (54% vs 54%, 28 events) |
| Bucket ladder rule (edges at floor(prev cents) minus 1 or 2, 6 or 7 edges) | MEASURED, not reproducible exactly | 28 events: offsets -1 (13), -2 (15) |
| Boundary-rule hit rates out of sample (71% / 88% depending on ladder) | MEASURED but ladder assumed | gasw/oos_boundary.py, DESIGN-amendment-2 |
| Fills at the favourite's own ask before 03:15 ET | UNMEASURED: only one event (19 Nov: ask 0.998, depth at or below 0.97 = 0) | books file us-gas-price-on-november-19-2026 |
