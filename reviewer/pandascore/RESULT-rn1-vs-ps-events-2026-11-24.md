# RESULT R-093: RN1 CS2 fills vs PandaScore kill / round-end messages (24 Nov 2026, paper, read-only)
Script feeds/rn1_vs_ps_events.py (fills pulled from data-api v2 /trades with user= AND condition_id=, every row asserted to be his wallet and the requested market; taker = taker_only=true, maker = taker_only=false minus true). Output: reviewer/pandascore/RESULT-rn1-vs-ps-events-2026-11-24.json.

**Verdict: OVERLAP COUNT 0 for taker fills.** In the 29 Polymarket markets (moneyline + Map N) of the 15 PandaScore sample matches (19-20 Nov), RN1 (0x2005d16a...) has **0 taker fills at any time**, so the question "do his takes cluster before or after public events" CANNOT be answered from these matches. It is a statement about overlap, not about speed.

| match_id | match | RN1 taker fills in window | RN1 maker fills in window | PS kill + round-end events |
|---|---|---|---|---|
| 1789179 | 33 v ex-RUSTEC | 0 | 0 | 42 |
| 1789181 | ex-INOX Division v FORZE Reload | 0 | 0 | 429 |
| 1789182 | aimclub v Nexus | 0 | 0 | 305 |
| 1789185 | Rune Eaters v Butterfly | 0 | 0 | 71 |
| 1791306 | Sangal v Luminosity | 0 | 0 | 256 |
| 1791309 | GamerLegion v Inner Circle Esports | 0 | 0 | 307 |
| 1791310 | BIG v NIP | 0 | 0 | 356 |
| 1791311 | GamerLegion v BIG | 0 | 0 | 102 |
| 1791312 | Luminosity v BIG | 0 | 0 | 234 |
| 1796498 | Brute v Nice Try | 0 | 0 | 68 |
| 1796512 | Iberian Soul v Butterfly | 0 | 0 | 90 |
| 1803639 | Apogee Esports v maybe | 0 | 0 | 87 |
| 1803646 | WBT v MOUZ NXT | 0 | 0 | 399 |
| 1803648 | ex-INOX Division v WBT | 0 | 0 | 164 |
| 1805735 | Envy v Nexus | 0 | 65 | 31 |

What exists: 65 of his MAKER fills fall inside the match windows (111 maker rows in these markets in total, all 20 Nov 15:19-16:21Z). Against the same events (fill time minus event time, +-60 s, 1 s bins; fill timestamps are whole seconds): 6 maker fills in the 10 s before an event, 2 in the 10 s after; random times inside the same match spans give 5.6 and 5.6 (sd about 3.6). That is inside the placebo range: no timing pattern, and makers are the class the Reviewer said to use only as a placebo.

Why no taker overlap: the Reviewer's 1,254 taker fills are from 73 CS2 matches over 30 days; none of those fall in the 15 matches for which a PandaScore capture exists (the capture was down 16-19 Nov and again since 22 Nov 21:51Z, P118). To answer R-093 we need PandaScore messages on days he takes CS2: first step is the capture running (IT P118) and a list of his CS2 take days (from his fills, public) to compare with capture days; I can produce that list on request. Confidence 9/10 that the overlap is 0 (56 fill files fetched live today, each asserted); 3/10 that his takes are not faster than PandaScore (no data).
