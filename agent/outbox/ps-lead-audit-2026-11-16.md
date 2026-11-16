APPROVALS NEEDED: none. Read-only audit; no code, collector, or live process changed.

RESULT — sim on real data; code commit under audit: `d36a286d78` (script SHA-256 `90a55fd8e8e9d4eade0802e2ee727275826e38e12de93ad4f3f7f1d21e845587`).
- Independent session: this 02:32Z PK audit session did not run `ps_lead_test.py`; the registered test was run at 01:33Z. Audit exited 0 in 10.22s; peak RSS 88,096 KiB.
- A, all-event / isolated (nearest same-match event gap >=60s): CS2 map — n=424; Δmed=-28.17s; after/onset=11.7%; after/all=8.3%; no lead reproduced / n=398; Δmed=-25.71s; after/onset=12.0%; after/all=8.5%; no lead reproduced.
- A, all-event / isolated: CS2 match — n=528; Δmed=-31.15s; after/onset=12.5%; after/all=7.8%; no lead reproduced / n=498; Δmed=-18.37s; after/onset=12.1%; after/all=7.6%; no lead reproduced.
- A, all-event / isolated: Dota map — n=979; Δmed=-45.09s; after/onset=18.6%; after/all=9.8%; no lead reproduced / n=36; Δmed=40.58s; after/onset=37.5%; after/all=16.7%; not confirmed as no-lead.
- A, all-event / isolated: Dota match — n=1114; Δmed=-42.70s; after/onset=30.8%; after/all=14.0%; no lead reproduced / n=43; Δmed=-33.08s; after/onset=0.0%; after/all=0.0%; no lead reproduced.
- A gap buckets (each `n/onset; after-feed % among onset`): CS2 map 0–10 0/0; —, 10–30 0/0; —, 30–60 26/16; 6.3%, >=60 398/284; 12.0%. CS2 match 0–10 0/0; —, 10–30 0/0; —, 30–60 30/14; 21.4%, >=60 498/314; 12.1%.
- A gap buckets: Dota map 0–10 569/299; 19.1%, 10–30 243/128; 15.6%, 30–60 131/73; 17.8%, >=60 36/16; 37.5%. Dota match 0–10 652/307; 32.2%, 10–30 276/122; 30.3%, 30–60 143/63; 31.7%, >=60 43/15; 0.0%.
- B, 23 event-bearing match IDs: PS increases / any-change = CS2 rounds 598/598; Dota kills 989/989, towers 223/223, barracks 68/68, Roshan 33/38. Recount restricted to those IDs: rounds 697; kills 1,069; towers 243; barracks 76; Roshan increases 38. Differences are -14.2%, -7.5%, -8.2%, -10.5%, -13.2%; unexplained under the 2% rule.
- B, missing among the 26 recount IDs relative to the exact 23 audited IDs: 1785760, 1789157, 1803636. Largest per-match gaps: rounds 1762448 (-21), 1796496 (-19); kills 1793319/1791800 (-40 each); towers 1791800 (-13); barracks 1793319/1791800 (-4 each); Roshan 1791800 (-3).
- C, no fuzzy join: Apogee Esports vs Leo Team (40 PS events; no token candidate); Hype Tech vs Phantom (9; none). BAKS Esports vs EX-Zero Tenacity (21; candidate Zero Tenacity appears only with PuckChamp; likely sponsor/name-token mismatch, not a verified pairing).
- C: Inner Circle x Insanity vs Nemiga Gaming (121; candidate Inner Circle Academy appears with Omega, not a verified pairing); PARIVISION vs Yellow Submarine (78; candidate Yellow Submarine appears with DO KONCA, opponent mismatch). No obvious exact pairing established; no additions made.
- Audit-script disagreements: its `pct_price_after_feed` divides by events with a detected onset, while STANDARD v1 says percentage of events; report includes both after/onset and derived after/all. Its directory-ID helper says one recount ID absent because it includes extra PS directory IDs; the locked comparison on 23 event-bearing IDs yields three missing above. Decision words above use the locked all-event denominator.

DATA
- Full calculated evidence: `agent/status/pandascore-lead-audit-2026-11-16.json` (A cells/buckets, B per-match rows, C market-token candidates).
- Raw run output and resource proof: `/vol2/pkarbs/scratch/ps-lead-20261115/audit-20261116.{json,stdout,stderr}`; volume source provenance not independently checked.

OPEN / NOT VERIFIED
- Volume-map source/provenance; no volume-stratum audit. No fuzzy market pairing was approved or applied.

Count: notes run 1, outstanding 0, PENDING open 0
