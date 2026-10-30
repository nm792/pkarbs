# Headless render test — tennis + CS2 scores, 2026-10-30

Task `agent/TASK-render-test-2026-10-30.md`. The task's prescribed tooling (playwright at `/opt/pw-browsers/chromium`) is **not installed** on the server, so the pages were rendered with a real headless browser driver (equivalent capability, honest UA `pkarbs-research/1.0 (contact nm@delphic.co)`, no stealth). Robots for all three match paths were verified allowed earlier (coverage task). 3 pages rendered, ≥5 s apart, one process.

## Request log (URL | status | bytes | delay)
| ts UTC | URL | status | bytes |
|---|---|---|---|
| 06:30 | https://www.wtatennis.com/scores (+ Rybakina-v-Fernandez final) | 200 | 210,433 |
| 06:31 | http://www.tennisabstract.com/cgi-bin/player.cgi?p=126205/Tommy-Paul | 200 | 44,390 |
| 06:32 | https://bo3.gg/matches/gotei-5-vs-underworld-26-10-2026 | 200 | 12,827 |
Delays ≥5 s. No 403/429/5xx/challenge encountered.

## Render results (parsed from the rendered DOM)
| # | source | match | in-window 22-29 Oct? | final scores parsed? | details |
|---|---|---|---|---|---|
| 1 | wtatennis.com | (1) Elena Rybakina d. Leylah Fernandez, Ningbo Open final | **yes — 25 Oct** | **YES** | rendered scores **6-2, 6-2** (set and game level); both players read from the match page |
| 2 | tennisabstract.com | (7) Tommy Paul d. (30) Andrey Rublev, Vienna R32 | **yes — 26 Oct** | **YES** | rendered row `26-Oct-2026 Vienna Hard R32 (7)Paul d. Andrey Rublev [RUS] 7-5 6-2` — set scores present |
| 3 | bo3.gg | gotei 5 v Underworld, Gamers Club LSA Oct | **yes — 26 Oct** | **NO** | final shows `1 - 2` (matches external sites' result) but **per-map scores are blank `0 - 0` / "There are currently no data"** — bo3 renders the matchup but does NOT serve map/round scores on this page |

## PASS / FAIL
- **TENNIS: PASS** — 2 of 2 tennis matches (1 WTA + 1 ATP, both 22–29 Oct) have game-level set scores on the rendered pages. Covers the two rn1-heavy tours.
- **CS2: FAIL** — bo3.gg renders (no error) but serves no map/round scores for the in-window match (blank `0-0`). CS2 score coverage remains open.
- **Task rule (≥2 of 3 pages with parsed scores): PASS (2/3).** No 403/429/5xx/bot-challenge (which would force FAIL).

## Verdict for the reviewer
- **WTA is a usable, robots-allowed, render-parsed score source** for rn1's tennis (% of slugs: ATP-heavy, but the site matches news/other sources — 6-2 6-2).
- **Tennis Abstract is a strong historical source** — its player results page already carries per-match set scores in HTML (no render even needed); this is the best ATP/Challenger source found.
- **CS2 (bo3.gg) is not usable for per-map/round scores** even rendered — the page ships blanks. A browser-driven API call (`/api/…`) is disallowed by its robots.txt, so CS2 stays uncovered under these rules.

## Raw HTML
Committed under `reports/render-test/raw/` (wta-scores.html, tennisabstract-paul.html, bo3-gotei5-underworld.html).

## Cleanup
Browser closed; no processes remain. `ps` own procs: none (logger pid 2951556 unrelated).
`free -m`:
```
               total        used        free      shared  buff/cache   available
Mem:            7746        3034        539          50        4531        4711
```

No IPs, host names, volume names or keys.