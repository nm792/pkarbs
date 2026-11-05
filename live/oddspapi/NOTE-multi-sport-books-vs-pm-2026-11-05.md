# Bookmaker (Pinnacle, bet365) lead vs Polymarket price, 6 sports, with and without the 0.3 s ack guard
5 Nov 2026, 07:15Z. Nick: "Can we not try the odds feed on past matches of other sports?" and "the slow-order guard will matter if the OddsPapi feed shows a similar outcome for the esports". Confidence 6/10.

Data: OddsPapi history (free), the 60 most recent finished matches per sport up to 4 Nov (408 of 429 pulled), matched to Polymarket moneylines by team name and traded prices from data-api. NBA 54 matched, NHL 56, NFL 41, LoL 35, CS2 37 (18 with enough Pinnacle data), Dota 42 (32). Cricket and rugby: **not yet**: Polymarket lists cricket moneylines only up to 29 Oct and Premiership/URC rugby up to about 10 Oct (plus a few on 23 Oct), so none of the recent OddsPapi matches overlapped. A second pull for that window is with Hermes (TASK-oddspapi-multi2).

Method: cross-correlation of 5 s price changes on a 1 s grid (placebo = book shifted 900 s); trigger backtest: book step >= 1.5 pp -> bid PM at mid-2.5% on that side for 5 s, hold to resolution, 500-share cap, order latency drawn from the 30 measured Nautilus acks (median 0.2 s, p90 1.3 s). Guard = cancel when the ack takes over 0.3 s (about 30% of signals). Fills are trade-based and ignore the queue (optimistic). $/day is in-sample (matches per day in the sample, not whole-sport volume).

## Lead (positive = book moves first)
| sport | Pinnacle lead | peak corr (placebo) | matches | bet365 |
| --- | --- | --- | --- | --- |
| NBA | 1 s | 0.31 (0.005) | 54 | -1 s (later) |
| NFL | 1 s | 0.10 (0.01) | 41 | no usable data |
| LoL | 3 s | 0.07 (0.008) | 35 | 22 matches, no peak (0.006) |
| CS2 | 4 s | 0.20 (0.01) | 18 | 8 matches, no peak |
| Dota | 3 s | 0.05 (0.009) | 32 | 6 matches, no peak |
| NHL | unreliable (-45 s at corr 0.2 vs 0.02 at 0 s) | | 56 | none (0.014) |

## Backtest at measured order speed ($/match; 90% range; without top 5)
| sport / book | no guard | with 0.3 s guard | without top 5 (guard) | $/day (guard) |
| --- | --- | --- | --- | --- |
| Dota Pinnacle | 46 [5, 102] | 41 [2, 96] | -3 | 96 |
| LoL Pinnacle | 48 [-202, 248] | 30 [-199, 210] | -106 | 51 |
| CS2 Pinnacle | 7 [-23, 38] | 17 [-20, 56] | -15 | 59 |
| NFL Pinnacle | 28 [-4, 65] | 23 [-8, 57] | -12 | 58 |
| NBA Pinnacle | -134 [-238, -46] | -122 [-227, -38] | -147 | negative |
| NBA bet365 | -98 [-165, -36] | -89 [-154, -32] | -107 | negative |
| NHL Pinnacle | -1 (3 of 56 filled) | -1 | -1 | ~0 |
bet365 in LoL, CS2, Dota, NFL, NHL: no fills (too little data).

## Reading
1. Pinnacle leads Polymarket by about 3-4 s in the esports and 1 s in NBA/NFL, clearly above the placebo. bet365 shows no lead anywhere it has data.
2. The profit is concentrated: every result drops to zero or below when the top 5 matches are removed, and every esport range spans zero except Dota without guard and with guard (+$2 to +$96), which still loses $3/match without its top 5.
3. The guard is not a consistent win: it helps CS2 (+$10) and NBA (smaller loss), hurts LoL (-$18), Dota (-$5), NFL (-$5). With a 3-4 s lead and a 0.2 s typical order, only the rare slow order (1 in 10 over 1.3 s) matters, and cancelling at 0.3 s also cancels good orders. Do not switch the LoL guard on because of this test.
4. NBA/NHL loses heavily because the plain trigger buys every book move without an event filter (the PM price has already moved); not a sport to use this way.
5. The practical limit is unchanged: we only get Pinnacle live through OddsPapi's paid websocket (B2B plan); free REST is 0.5 s per fixture, too slow for a 3 s lead.

Files: winmodels/multi_lead.py, winmodels/out_multi_lead.json, live/oddspapi/pull_hist_multi.py, rn1/scores/oddspapi/multi-2026-11-05/.
