APPROVALS NEEDED: none. Read-only audit; no code or live process changed.

RESULT — sim on real data; audited code `feeds/ps_lead_audit.py` at `ef40e8c268b16d0fee16c82016785c360097d33c`, SHA-256 `c74a195564966a4ff0bb0b75483cc56e7b88f776c97d9d91f450d039bb5304db`. Independent 02:54Z session, not the 01:33Z test session. Audit exited 0 in 11.02s; peak RSS 90,648 KiB.

A. `n / median(real−placebo) s / price-after-feed % of all events / locked word`:
| Title | Series | All events | Isolated (nearest same-match event ≥60s) |
|---|---|---|---|
| CS2 | map | 424 / -63.20 / 8.3% / no lead reproduced | 398 / -39.53 / 8.5% / no lead reproduced |
| CS2 | match | 528 / -13.46 / 7.8% / no lead reproduced | 498 / -19.34 / 7.6% / no lead reproduced |
| Dota 2 | map | 979 / -6.12 / 9.8% / no lead reproduced | 36 / +25.53 / 16.7% / not confirmed as no-lead |
| Dota 2 | match | 1,114 / +15.19 / 14.0% / not confirmed as no-lead | 43 / +16.59 / 0.0% / not confirmed as no-lead |

Gap buckets are `events/onset/after; after as % of all events`, in order `<10s, 10–<30s, 30–<60s, ≥60s`: CS2 map `0/0/0 n/a, 0/0/0 n/a, 26/16/1 3.8%, 398/284/34 8.5%`; CS2 match `0/0/0 n/a, 0/0/0 n/a, 30/14/3 10.0%, 498/314/38 7.6%`; Dota map `569/299/57 10.0%, 243/128/20 8.2%, 131/73/13 9.9%, 36/16/6 16.7%`; Dota match `652/307/99 15.2%, 276/122/37 13.4%, 143/63/20 14.0%, 43/15/0 0.0%`.

**CRITICAL — placebo comparison is not reproducible:** a second same-input run kept event counts, real medians and after-feed fractions, but changed placebo medians because the script iterates sets before using its seeded RNG. `median(real−placebo)` and its dependent words therefore vary by run; the figures above are the first run and provisional pending an order-stable audit. Also, script `pct_price_after_feed` uses only events with an onset; the locked rule uses all events, as recalculated here. No code was changed.

D. Feed clock `recv_ns`; PM price clock book-row `ms`; both capture-host clocks. `updated_at`/`sent` are not used for lead. Chrony: stratum 3, system 0.000153s fast, leap Normal (02:54Z). Prior test report: PM `ms−sent` median 156ms, P90 422ms, range 52–8,571ms over 520,905 rows. `recv_ns−updated_at` seconds p10/median/p90/max: CS2 other n=9,093 `0.053/0.067/0.103/34.083`; CS2 event n=598 `0.052/0.067/0.104/14.191`; Dota other n=11,918 `0.045/0.053/0.081/21.208`; Dota event n=1,275 `0.046/0.054/0.079/0.688`. CS2 all-players-dead→round-score increase n=122: `0.000/11.158/151.956/484.253s`; receipt-time difference, not isolated vendor delay.

B. PS increases/any-change: rounds `598/598`; kills `989/989`; towers `223/223`; barracks `68/68`; Roshan `33/38`. Recount restricted to same 23 IDs: rounds 697, kills 1,069, towers 243, barracks 76, Roshan 38; PS shortfalls 14.2%, 7.5%, 8.2%, 10.5%, 13.2%, **unexplained** under 2%. Three recount IDs absent: 1785760, 1789157, 1803636. Largest recount-minus-PS gaps: rounds 1762448 +21, 1796496 +19; kills 1793319/1791800 +40 each; towers 1791800 +13; barracks 1793319/1791800 +4; Roshan 1791800 +3.

C. Unmatched; no fuzzy joins: Apogee Esports–Leo Team (40 events, no candidate); BAKS Esports–EX-Zero Tenacity (21; Zero Tenacity candidate only vs PuckChamp in Dota, not verified); Hype Tech–Phantom (9, no candidate); Inner Circle x Insanity–Nemiga Gaming (121; Inner Circle Academy candidate vs Omega, different opponent); PARIVISION–Yellow Submarine (78; candidate vs DO KONCA, different opponent). Possible alias/spelling relationships unverified; no additions.

DATA
- Full A/B/C/D calculations: `agent/status/pandascore-lead-audit-2026-11-16.json`.
- Raw run/resource proof: `/vol2/pkarbs/scratch/ps-lead-20261115/audit-20261116-D.{json,stdout,stderr}`.

OPEN / NOT VERIFIED
- Placebo comparison needs an order-stable rerun. Volume-map provenance and STANDARD section-4 P&L spread, top-3 concentration, cluster-robust t, variant correction, and first-print log score were not checked. No volume-stratum/money-bar result or pass/fail conclusion.

Count: notes run 1, outstanding 0, PENDING open 0
