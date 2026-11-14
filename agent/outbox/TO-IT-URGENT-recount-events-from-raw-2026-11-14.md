# P14 #318 raw-data recount — 14 Nov 2026 11:16Z

Read-only recount completed with the existing `/vol2/pkarbs/scratch/p318-recount/recount.py`; exit 0. No code, feed, or rule changed. Windows start 13 Nov 15:12:29Z (PandaScore) and 15:09Z (Goalserve). See coverage caveat below.

## A. PandaScore status-diff events

21 matches in the selected files (12 CS2 and 9 Dota 2) contain real state transitions. This corrects the earlier 04:15Z zero-event conclusion: that count inspected lifecycle-only `events.jsonl.gz`, not raw status snapshots. Dota figures below are counter increases. CS2 score counts changed team-side score fields; alive counts boolean flips.

| Match ID | Title | Rows | Kills | Towers | Barracks | Roshan | CS2 score | CS2 alive | >60s gaps | Max gap (s) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1762447 | Spirit vs MOUZ | 394 | 0 | 0 | 0 | 0 | 26 | 258 | 1 | 125.654 |
| 1762448 | FURIA vs Team Falcons | 61 | 0 | 0 | 0 | 0 | 0 | 6 | 1 | 138.849 |
| 1785753 | PuckChamp vs Zero Tenacity | 1906 | 141 | 28 | 8 | 4 | 0 | 0 | 7 | 903.811 |
| 1785771 | Team Allied vs potn9ki | 1619 | 127 | 25 | 6 | 4 | 0 | 0 | 4 | 943.794 |
| 1786827 | Omega vs Inner Circle Academy | 1093 | 0 | 0 | 0 | 0 | 79 | 758 | 6 | 733.050 |
| 1786828 | Apogee Esports vs Leo Team | 579 | 0 | 0 | 0 | 0 | 48 | 425 | 5 | 581.999 |
| 1789156 | ex-Zero Tenacity vs BakS eSports | 271 | 0 | 0 | 0 | 0 | 21 | 223 | 5 | 130.044 |
| 1789157 | FORZE Reload vs Walczaki | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.025 |
| 1789158 | ex-RUSTEC vs Nexus | 633 | 0 | 0 | 0 | 0 | 45 | 474 | 4 | 762.296 |
| 1791798 | Froglings vs PuckChamp | 452 | 36 | 15 | 7 | 1 | 0 | 0 | 5 | 621.799 |
| 1791799 | CyberHero vs Xipto Esports | 1251 | 122 | 21 | 6 | 3 | 0 | 0 | 7 | 624.522 |
| 1791800 | Inner Circle x Insanity vs Nemiga Gaming | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 31.361 |
| 1793318 | PARIVISION vs Yellow Submarine | 524 | 61 | 12 | 4 | 1 | 0 | 0 | 0 | 49.570 |
| 1793323 | LGD Gaming vs LEGION | 968 | 51 | 7 | 0 | 2 | 0 | 0 | 3 | 3651.436 |
| 1793327 | Team Spirit vs Froglings | 1550 | 127 | 28 | 7 | 6 | 0 | 0 | 6 | 3562.839 |
| 1796489 | FORZE Reload vs Nice Try | 328 | 0 | 0 | 0 | 0 | 20 | 87 | 2 | 99.027 |
| 1803635 | GenOne vs Balkan Outlaws | 449 | 0 | 0 | 0 | 0 | 31 | 347 | 2 | 3619.246 |
| 1806970 | Team Liquid vs LGD Gaming | 2267 | 158 | 39 | 15 | 6 | 0 | 0 | 5 | 1305.641 |
| 1809115 | STATE vs BBL | 853 | 0 | 0 | 0 | 0 | 54 | 242 | 3 | 623.541 |
| 1809116 | LUNTIKI vs 33 | 1187 | 0 | 0 | 0 | 0 | 76 | 356 | 9 | 735.026 |
| 1809117 | STATE | 1488 | 0 | 0 | 0 | 0 | 82 | 932 | 9 | 3405.860 |

Totals: Dota kills 823, towers 175, barracks 53, Roshan 27; CS2 score-side changes 482, alive flips 4108. These are snapshot transitions, not unique scoring events.

Close errors: 4,553 total: code 4004 = 4,549, missing code = 4. All 4,549 coded errors are match 1789154; missing-code rows are 3 for 1789154 and 1 for 1793327. Receive gaps >60s occur in multiple live matches (table), max 3,651.436s. The data shows stale intervals but not causality: churn-caused data loss is neither proven nor ruled out.

## B. Goalserve odds payload changes

Counted changed participant payloads for consecutive `value_eu`/`suspend` values by match/market, not individual field flips.

| Match ID | Match | Payloads | Changed payloads |
|---|---|---:|---:|
| 140832465 | KUUSAMO vs MayBe | 6063 | 7076 |
| 141116256 | Alliance vs Four Magic | 3362 | 4352 |
| 141163317 | Apogee vs Leo Team | 3295 | 3504 |
| 141164392 | MayBe vs mixLVLT | 2519 | 3386 |
| 141164409 | Saint Sinners vs Balkan Outlaws | 297 | 306 |
| 141164753 | ex-RUSTEC vs Nexus | 3244 | 4322 |
| 141164775 | Omega vs Inner Circle Academy | 5100 | 6129 |
| 141165637 | Froglings vs PuckChamp | 1898 | 774 |
| 141165643 | CyberHero vs Xipto | 4045 | 3470 |
| 141165675 | PARIVISION vs Yellow Submarine | 1299 | 640 |
| 141165682 | Team Liquid vs LGD Gaming | 6742 | 2577 |
| 141165693 | Team Spirit vs Froglings | 4348 | 2806 |
| 141192093 | STATE vs EYEBALLERS | 1922 | 2149 |
| 141199605 | Noir Verse vs 6yuBoJlbl | 3102 | 3654 |
| 141199608 | Lavked vs Alliance | 2999 | 3968 |
| 141199612 | ex-INOX vs Saint Sinners | 2612 | 3195 |
| 141202857 | GenOne vs Balkan Outlaws | 2339 | 2998 |
| 141216876 | LGD Gaming vs Legion | 2339 | 1658 |
| 141216926 | Team Spirit vs MOUZ | 1882 | 18022 |
| 141216927 | Inner Circle vs Nemiga | 449 | 84 |
| 141216970 | FURIA vs Falcons | 417 | 3042 |

Total 78,112 changes across 21 matches and 19 hourly files: CS2 62,908; Dota 2 12,009; other esports 3,195. One malformed row skipped.

## D. Polymarket books and volume strata

Since 13 Nov 17:06Z: 345 registered matches / 1858 tokens; 1022334 book rows; 90 matches with rows; 0 malformed book rows. Of 21 PandaScore matches, 18 joined a registered PM market and 3 did not.

| Sport | Volume stratum | Book-covered matches | Book rows |
|---|---:|---:|---:|
| CS2 | <25k | 220 | 586041 |
| CS2 | >=25k | 5 | 126691 |
| Dota 2 | <25k | 118 | 245567 |
| Dota 2 | >=25k | 2 | 64035 |

Captured trade notional (price × size), same window: 338 registered matches <$25k and 7 >=$25k; 41 matches had trades (19772 trade rows).

## Coverage caveat

The existing script explicitly excludes `pandascore_2026111410.jsonl.gz` and `esports_2026111410.jsonl.gz`; therefore these results do not include the completed 10:00–11:00Z hour and are partial relative to the requested complete raw window. It also read the live 11:00Z append hour, where one malformed PandaScore row and one malformed Goalserve row were skipped. No full-window verdict is claimed.

Full included-window evidence: `agent/status/p318-recount-2026-11-14.json`. Execution log: `/vol2/pkarbs/scratch/p318-recount/run-20261114-1114.log`. No P&L, lead, or outcome calculated.
