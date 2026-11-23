# Thanksgiving Turkey Pardon 24 Nov 2026: per-word transcript base rate (R-071 item 2), built 23 Nov 14:45Z
Event: gamma id 1434437, "What will Trump or Melania say during the Thanksgiving Turkey Pardon?", speech 24 Nov 19:00Z, resolution = audio/video of the appearance only, 12 words. Paper only. NO LOOKAHEAD: only transcripts dated before 24 Nov 2026.

## Sources (read in full, 23 Nov)
- 21 Nov 2017, 20 Nov 2018, 26 Nov 2019, 24 Nov 2020: official White House remarks, trumpwhitehouse.archives.gov/briefings-statements/remarks-president-trump-national-thanksgiving-turkey-pardoning-ceremony (no suffix = 2017, -2 = 2018, -3 = 2019, -112420 = 2020). Lengths about 650 to 1,150 words.
- 25 Nov 2025: Compilation of Presidential Documents, govinfo.gov/content/pkg/DCPD-202501146/html/DCPD-202501146.htm (about 3,300 words). It is an EDITED official text ("[tallow; White House corrections]"), not audio, so a word could differ from the audio. Melania did not speak in the 2025 text.
- Not used yet: Melania remarks (none found), and "short WH remarks of similar length" from Nov 2026 (needs a transcript source; Roll Call Factba.se and Rev are the candidates; not read, so NOT included).

## Observations (1 = the word was said in that year's appearance; plural or variant noted)
| word | 2017 | 2018 | 2019 | 2020 | 2025 | note |
|---|---|---|---|---|---|---|
| Bean | 0 | 0 | 0 | 0 | 0 | |
| Potato | 0 | 0 | 0 | 0 | 1 | "Potatoes are down 13 percent": counts only if the market's full rules accept plurals (UNVERIFIED, the rules PDF was not read) |
| Tomato | 0 | 0 | 0 | 0 | 0 | |
| Chicken / Egg | 0 | 0 | 0 | 0 | 1 | "Egg prices are down 86 percent" |
| Iran | 0 | 0 | 0 | 0 | 0 | |
| Joe / Biden | 0 | 0 | 0 | 0 | 1 | "Sleepy Joe Biden", "Biden-era" |
| Xi / China | 0 | 0 | 0 | 1 | 0 | 2020: "China virus" |
| Ballroom | 0 | 0 | 0 | 0 | 0 | 2025 mentions a "new patio", not a ballroom |
| West Virginia | 0 | 0 | 0 | 0 | 0 | |
| Border | 0 | 0 | 0 | 0 | 1 | "our border", "southern border" |
| Poultry | 0 | 1 | 0 | 1 | 0 | "poultry science" (2018, 2020) |
| Drone / Helipad | 0 | 0 | 0 | 0 | 0 | |
Multi-word OR markets (Chicken / Egg, Joe / Biden, Xi / China, Drone / Helipad) are scored as YES if EITHER term appears, as the market lists them; the exact variant rules are in the full-rules PDF linked by the market, not read here (UNVERIFIED).

## Model and result
q = (wins + 2 x gp) / (5 + 2), gp = pooled hit rate 7/60 = 0.117 (same alpha = 2 shrinkage as the frozen rule); interval = 90% Beta posterior. POWER: 5 observations per word. This is a shrunk prior, NOT a tested edge; an interval from 5 observations is wide.
| word | wins of 5 | q | 90% interval |
|---|---|---|---|
| Poultry | 2 | 0.319 | 0.081-0.619 |
| Potato, Chicken/Egg, Joe/Biden, Xi/China, Border | 1 | 0.176 | 0.017-0.442 |
| Bean, Tomato, Iran, Ballroom, West Virginia, Drone/Helipad | 0 | 0.033 | 0.000-0.165 |

## WARNING: the base rate is blind to this year's topics (read before any item 3 scoring)
One snapshot of own-token best asks at 14:45Z (file q_and_asks_snapshot_2026-11-23T1445Z.csv; best ask only, NOT depth, NOT a decision): YES asks are West Virginia 0.94, Drone/Helipad 0.79, Joe/Biden 0.74, Ballroom 0.70, Xi/China 0.67, Border 0.65, Iran 0.60, Chicken/Egg 0.58, Poultry 0.37, Potato 0.32, Bean 0.26, Tomato 0.18. Against this base rate the 10c rule would fire NO on 9 of 12 words, with gaps up to 0.86 (West Virginia). A 50-85c gap from a five-observation prior is not an edge, it is model blindness: the market prices facts this base rate cannot see (where this year's turkeys come from, current news such as Iran, the ballroom, a drone or helipad, the Chicago and border themes of 2025). Words with 0 hits in 5 events have a prior of 0.03 only because they never came up in past speeches, not because they are unlikely in 2026. The frozen rule was tested on families where each word has its own long settled history; none of these topical words does.
So: (a) do NOT paper-trade this base rate against the 10c cell as an edge claim; (b) in item 3 report the result as "base rate vs market disagreement", with the gaps explained by topical information where it can be sourced; (c) the sensible use of the transcript prior is only for words that have both history and no new topical reason: Poultry, Potato, Bean, Tomato, Chicken/Egg. Of these the NO ask on Bean 0.82 vs q 0.97 (edge 0.147) and Tomato NO 0.86 vs 0.97 (0.107) are the only gaps near the 10c line, and each rests on 0 of 5 hits.
Confidence 7/10 on the observations (read in full; the 2025 text is edited); 2/10 that any word has a real edge.
