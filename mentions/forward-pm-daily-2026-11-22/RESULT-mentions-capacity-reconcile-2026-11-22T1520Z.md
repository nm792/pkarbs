# Mentions capacity reconcile (R-047, R-048, R-049), 22 Nov 2026 ~15:20Z. All runs off-Prime in a container, read-only public APIs.
Code: it/mentions_pm_open_depth.py (4 checks), it/mentions_pm_recent.py (3 checks), it/mentions_pm_depth_backtest.py (7 checks), it/mentions_pm_earnings_table.py (4 checks). Files: this folder.

## 0. Labels
$1.27/day (earnings calls) and $6.61/day (all) were print-capped fills: per R-034 they are NOT capacity figures. They stay only as "what printed". There is NO MEASURED $/day: no book was recorded at any decision time (firelog not installed, IT P103). Depth below is a SNAPSHOT of live own-token books, 22 Nov ~14:55-15:05Z, not decision time.

## 1. Every open mentions event (R-047 3; gamma tag mention-markets = 10 events; polymarket.com unreachable from this container, so NOT checked against the live /mentions page)
Edge-priced = own-token asks priced at or below fair - 10c (YES fair = q, NO fair = 1-q, causal history), >= 5c. Full = every ask level. Per token rows: open_1500_tokens.csv (URL, side, fair, best ask, full $, edge $, levels, market 24h/total volume).
| event (family) | Gamma 24h | Gamma total | full-ladder ask $ (all tokens) | edge-priced ask $ (all tokens, event) | edge-priced best single token |
|---|---|---|---|---|---|
| Salesforce earnings (earnings) | 4,046 | 4,046 | 47,520 | 264 | 130.92 |
| Deere earnings | 964 | 964 | 21,407 | 190 | 57.95 |
| Dell earnings | 901 | 901 | 37,998 | 98 | 43.35 |
| Trump/Melania Thanksgiving pardon (trump) | 3,896 | 13,088 | 97,951 | 1,348 | 299.49 |
| Trump at China APEC | 10 | 18,431 | 18,798 | 19 | 18.52 |
| Trump in the Philippines | 12 | 3,351 | 2,866 | 11 | 10.60 |
| Trump in November 2026 | 139 | 9,535 | 50,189 | 37 | 19.60 |
| Caedrel Worlds final stream (other) | 0 | 21,884 | 4,796 | 0 | 0 |
| Announcers Cowboys-Packers | 0 | 5,519 | 3,009 | 0 | 0 |
| Announcers Seahawks-Broncos | 0 | 5,408 | 996 | 6 | 5.71 |
Reconciles with the Reviewer snapshot (README: Salesforce $47,745, Thanksgiving $98,131, Deere $22,220, Dell $37,998): full-ladder totals agree within 1-2% (books moved in 7 minutes). My earlier "$43-131 none can take $200" was the edge-priced best token, correctly labelled in P-MEN-1455 as depth "at prices that keep the 10c edge", but the full ladder is 100x larger because most asks sit at 0.9+ (or <0.05) where there is no edge. Both are right; they measure different things.
**The $18-20K contract:** on Gamma no open contract has $18-20K 24h volume. Largest open single contract 24h is Salesforce "Fabric" $2,096. The $18-20K figures match EVENT lifetime totals: Trump at China APEC $18,431 and Caedrel final stream $21,884 (and Thanksgiving $13,088). Among recently closed events: Trump trilateral meeting (closed 19 Nov) $163,899 event total, $34,895 on its largest single contract. Cannot match to the live page from here.

## 2. R-048 deep dive (open_1500_deep.md has every strike's ladder)
**Caedrel Worlds final stream** (market start 12 Nov 00:00Z, end 15 Nov): Gamma total $21,884, 24h $0, liquidity $71. Own-token ask ladders: essentially empty (only 2 tokens had any asks; edge-priced $0). Trade-dated: 396 trades, $13,421 in the data API (61% of Gamma); $78 (0.6%) in the first hour, 15.5% in the first 24 h, 19% after day 3; busiest hour h+68 ($2,688) = about 14 Nov 20:00Z, i.e. at the final itself. **Frozen rule would NOT have bet** (no first-hour BUY print with edge >= 10c). Result n/a.
**Trump at China APEC** (start 17 Nov 17:15Z): Gamma total $18,431, 24h $10, liquidity $417. Ladders empty at the edge ($19 edge-priced event total). Trade-dated: 298 trades, $10,543 (57% of Gamma); $0 in the first hour (first trade 19:51Z, +2.6 h); busiest h+35, h+37 (19 Nov) and h+63. **Frozen rule would NOT have bet** (no print in the first hour).
Both events: volume prints around the event, not at listing; the rule's first-hour window sees 0-0.6% of it. Scope: the BACKTEST was NOT limited to earnings calls (917 events, all families). Only my per-call table and the snapshot depth work were earnings-only. Backtest bets by class since 1 Jan: Trump events 109 bets +$703; sports announcers 44 +$439; earnings 29 +$414; politician/official speeches and other (Walz, Mamdani, Vance, Starmer, Joe Rogan, Hegseth, Jensen Huang keynote...) 82 bets +$575; streamers/YouTubers 4 bets +$18.

## 3. R-049 recent windows, ALL families (recent_events.csv, one row per event; recent_summary.json)
| window | events closed | Gamma volume | trade-dated volume (data API) | of which last 24 h before end | last 6 h before end | bets (frozen rule, $200 cap, $2,000/day cap, print-based) | net | $/day | % of $200 |
|---|---|---|---|---|---|---|---|---|---|
| last 7 d | 16 | $258,544 | $161,873 | $66,127 | $2,446 | 3 | -$28.25 | -4.04 | -2.0% (FLOOR) |
| last 30 d | 67 | $1,526,644 | $849,087 | $278,772 | $89,634 | 21 | +$60.02 | +2.00 | +1.0% (FLOOR) |
Decision-time own-token ask depth for every event: UNMEASURED (no recorder). Bet side/price/size per event: columns bet_side, bet_word, bet_price, bet_size_usd, bet_pnl_floor in recent_events.csv.
**Weekly volume reconcile (Nick ~$100K):** trade-dated volume in the last 7 calendar days on ALL mentions events, open and closed, = **$142,484** (Trump events $120,089 + weekly $884 = 85%, earnings calls $18,241, other $3,267, announcers $3). Gamma lifetime volume of events that closed in the last 7 days = $258,544 (Reviewer's $222K uses a different cut-off). So Nick's ~$100K week is CONFIRMED, within the trade-dated $142K; no large gap. Gap I cannot explain: data-API trade notional is about 0.67x Gamma's reported volume (median over closed events above $5K; 0.57-0.61 for Caedrel and APEC), probably a definition difference (Gamma counts both sides or share-based); I use Gamma volume as the platform figure and the data API for timing. My earlier segment volume tables (P-017) were data-API based and are therefore about 1/3 low versus Gamma.
**Where the problem is: timing, not volume.** The rule enters in the first hour after listing; first-hour trade-dated volume on the big events is $24-368 (Trump midterm rallies $330K Gamma: $24 first hour; trilateral $164K: $234 first hour). Volume arrives at the event (final 24 h before end: $279K of the $849K). A capacity test needs either decision-time ladders in the first hour (firelog) or a rule variant that enters near the event: NOT tested; audit s.6 says 6 h and 24 h windows pass at 10c on the old bet-size, untested on capacity.

## 4. $/day restated at $200 per trade, $2,000/day cap, on snapshot edge-priced depth (ESTIMATE, not MEASURED; n = 10 events, tiny)
bets/day and return per $ staked taken from the backtest segment (trump .335/day, +43%; earnings .089/day, +113%; other .264/day, +58%; announcers .135/day, +69%), stake = min($200, edge-priced depth). ASSUMES the backtest return per $ holds at the larger size (unproven; each level is >= 10c under fair, so the edge floor holds, but fair may itself be wrong).
| family | (a) one bet per event, stake = min($200, best token) median / mean | (b) variant, all edge-priced tokens in the event up to depth, mean event, $2,000/day cap | note |
|---|---|---|---|
| earnings-call (3 open) | $5.85 (2.9%) / $7.82 (3.9%) | $18.59 (9.3%) | depth 43-131 best token |
| trump (4 open) | $2.74 (1.4%) / $8.93 (4.5%) | $50.83 (25.4%) | ONE event (Thanksgiving, $1,348 edge-priced) drives the mean |
| other (1 open, Caedrel) | $0 | $0 | no asks |
| announcers (2 open) | $0.26 (0.1%) | $0.28 (0.1%) | stale events |
Reading: the estimate ranges from about 4% (one bet per event) to a few tens of % (multi-token), decided by depth at the moment the rule fires, which no one has measured. (b) is a NEW variant, not the frozen rule.
