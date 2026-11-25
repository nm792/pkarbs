# Dota TheSports lead vs pmdota: scorer (spec SPEC-dota-thesports-lead-vs-pmdota-2026-11-25, STANDARD v1)

| File | Purpose |
|---|---|
| `dota_lead.py` | Format-agnostic core. It covers:<br>- events from normalized states (tower, roshan, barracks, fight = net kills >= 3 in 20 s);<br>- own-token mid onset and lead (STANDARD s.2);<br>- placebo, MC type 1: 10 event-free random times per match, random token and sign;<br>- plant, MC type 2: +3c step at t+5 s on 50% of events, and the run is void unless recovered within +-1 s;<br>- the s.3 bar per type, pooled only if every type has n >= 30, with a bootstrap by match. |
| `test_dota_lead.py` | 8 tests, all OK on 25 Nov:<br>- events and the fight rule;<br>- onset and lead sign;<br>- own book only;<br>- placebo is event-free;<br>- plant recovered;<br>- a plant at the wrong offset fails;<br>- bar cases (pass, n<30, negative, 50% after). |

**Still to add when P124b lands** (IT-OPS 2014Z, trading-test 122724f52):
- the TheSports box message -> normalized state adapter;
- the pmdota books row -> (t, bid, ask) adapter;
- the match join by team names plus start time, with unmatched games listed.

Each adapter gets a test from the real sample lines. Resolution: state the TheSports poll interval/2 and the pmdota cadence from the P124b read.

Placebo seeds use crc32 of the match key, so runs are reproducible.
