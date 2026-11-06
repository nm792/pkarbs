# Whole-project review, all sports (6 Nov 2026, 06:45Z)

Target: $500/day, several sports, automated, no catastrophic loss.
Strategy (fixed): after a game event, rest a post-only bid at market minus 2.5% on the side the model says should rise and has not, hold to resolution. We are not market makers.
Rules used here: every feed delay is quoted AGAINST THE POLYMARKET PRICE (when the price starts to move). "Measured" means observed live or on real trades. "Sim" means a backtest on trade history, which assumes fills and usually first place in the queue. Sim numbers are never called measured.
Sources: repo notes (winmodels/, live/, rn1/scores/, notes/), the shared folder, project memory up to 6 Nov 03:10Z. I did not re-run any analysis. Nothing here has been checked against Hermes status after 6 Nov 02:20Z.

## 1. Bottom line

1. **No sport is yet shown to make money at a feed we can actually get.** The best sim result is NBA at about $70/day on the free Polymarket stream. Every other sport is $0 at today's feed, or needs a feed we have not bought and not measured.
2. **We have zero live fills in any sport.** The only dry run (LoL DK-BLG, 6 Nov 02:48Z) placed 62 paper bids and got 0 fills. All dollar figures below are sim.
3. **The recurring blocker is feed speed against the price, not the model.** For LoL, CS2, Dota, NHL, NFL, tennis and cricket the free feed arrives after the price has already moved. Only NBA has a free feed (the Polymarket stream) that arrives while the price is still moving.
4. **Reaching $500/day needs two or three sports working at once.** On the best credible numbers: NBA ~$70-145/day plus a fast feed for LoL or Dota. Both are unproven. See section 5.

## 2. Volume (measured, 20 Oct-4 Nov, 15 days, gamma closed events, 230 leagues, $124.7M/day total)

| Sport | Total $/day | In-play $/day | Note |
|---|---|---|---|
| Soccer (166 leagues) | $35.1M | $19.2M | dropped 3 Nov, rn1 heavy |
| Esports (LoL, CS2, Dota, Valorant) | $29.1M | $24.8M | |
| Basketball (NBA $27.7M of it) | $28.8M | $14.3M | NBA in-play 50% |
| Tennis (ATP, WTA, ITF) | $14.5M | $13.1M | 91% in-play |
| American football (NFL $8.8M, CFB $3.7M) | $12.5M | $7.6M | |
| Ice hockey | $2.0M | $0.5M | |
| Baseball (MLB) | $1.3M | $0.9M | |
| MMA (UFC) | $0.9M | $0.8M | |
| Cricket | $0.5M | $0.4M | IPL is the big window |
| Rugby, golf, darts, handball, volleyball | ~$0 in window | n/a | outrights excluded; golf ~$174M/yr, Masters week ~$6-7M/day |

By league: NBA $27.7M, LoL $11.7M, CS2 $11.1M, NFL $8.8M, ATP $8.6M, Dota $6.1M, UCL $6.0M, WTA $5.6M. In-play share from 10-40 sampled events per league. Gamma volume is about 2x v2 trade notional. Full list: sports-volume/ADV-2026-10-20_11-04.md.

## 3. Sport by sport

Columns: feed delay vs price (measured), best known feed and cost, result, status, next step, date at risk. Result = sim unless stated.

### Esports and basketball: the three live candidates

**NBA** (in-play $13.8M/day, rn1 share 0.09%)
- Feed (measured, 1,320 score changes, 3 Nov, plus 32 on 4-5 Nov): the Polymarket sports stream arrives about 5 s after the play, which is 1-2 s BEFORE the price is half-moved (38-46% of the move already done). Free. NBA official S3 play-by-play: 7.8 s after the play (+0.8 s vs price half-move). ESPN summary: ~38 s, useless.
- Result (sim, 429 games, queue-safe fills): 0 s $25.6/game (~$184/day), 2 s $20.2 (~$145/day), 5 s $9.6 (~$69/day, range just spans zero), 10 s $2.9, 30 s+ negative. The stream earns ~$10/game (~$70/day). 2026-season held-out games disagreed held to result (-$42/game at 0 s on 39 games), a warning.
- Queue (measured, only 5 min of late-game books): median 6,300 shares ahead of our bid. This is the main uncertainty.
- Bookmaker route (Pinnacle, bet365): loses -$89 to -$134/match. Do not use.
- Faster feed: Sportradar custom contract from about $10k/month (unverified), Goalserve NBA live listed at $250/month, no published latency. Nick is asking vendors.
- Status: capture OFF until Nick releases it. Next: full-night 1 s books on 14 games (agent/tasks/nba-books-ws.md) to settle queue and price timing. Date at risk: none, season runs to April.

**LoL** (in-play $10.2M/day, rn1 0.03%)
- Feed (measured): Polymarket stream median 17.6 s AFTER the price (10-90%: -2.7 to +52 s, DK-BLG, 38 kills). Riot ~45 s. Our bids reach the book ~20 s after the price. The price had already moved on 35 of 38 kills.
- Result (sim, holdout 531 games, 500 cap): +$10.7k with a 2-22 s lag, +$6.3k at 20 s, but the 90% range at 20 s is -$3.0k to +$15.5k (spans zero). Per game $48-76 with the earlier assumption. Pinnacle leads the price by ~3 s, but LoL results spanned zero and lost $106/match without the top 5.
- Dry run (measured, 1 match): 62 paper bids, all rule-compliant, 0 fills, median queue ahead 1,876 shares.
- Best known feed: TheSports, $200/month for LoL, claims 2-3 s typical, no ms timestamps, trial includes a WebSocket. Not yet approved, not yet measured.
- Status: live pilot DRY ONLY (5 shares/order, $5/match, $20 loss cap, needs LIVE_OK). Next: T1 vs KC, 22:00Z 6 Nov = second dry sample. Date at risk: **Worlds final 14 Nov, then off-season to about mid-Jan.** A TheSports trial started ~6 Nov gives only ~8 days of LoL.

**Dota 2** (in-play $5.8M/day, rn1 0%)
- Feed (measured, 8 games, 4 Nov): Valve's free feed is 135-1,463 s behind the price (kill/tower events median 346 s). Polymarket stream: map score only, ~120 s cadence, +53 s after the price on one game. OpenDota 120-900 s.
- Result (sim, 344 games, first in queue, 100 cap): $12/game at 0 s, $7.5 at 20 s, ~$7 at 60 s, ~$0 from 90 s. About $270/day at 20 s, $430/day at 0 s if scaled to 18 games/day (estimate). Free feed is >= 180 s late, so $0 today.
- Pinnacle leads ~3 s; Dota Pinnacle +$41/match with guard but -$3 without the top 5.
- Feeds: TheSports $200/month; GRID (official BLAST/ESL data) company-only, rejected 4 Nov; PandaScore rejected 2 Nov (EUR 400-1,000/game/month).
- Status: capture OFF until released. Next: measure the TheSports feed against price during BLAST. Date at risk: **BLAST Slam 17-29 Nov** is the first real test; DreamLeague 2-13 Dec.

**CS2** (in-play $8.7M/day, rn1 3.8%)
- Feed (measured, 503 rounds): the Polymarket stream is 15-20 s behind the price; ~78% of the move is done when the round reaches us. Queue is not stale; bots reprice within about 1 s. Bookmaker lead: Pinnacle ~4 s, CS2 result +$17/match with guard, -$15 without top 5. Cito (cancelled 5 Nov) was ~193 s late.
- Result (sim, 20 matches): about $0 per match, range -$20 to +$25. rn1-style resting bids are break-even. Lower tier ~$0/day.
- Best known feed: TheSports $200/month; HLTV scorebot (only via Hermes); GRID rejected.
- Status: capture OFF until released; capped pilot built (PR #51/#53, needs LIVE_OK). Firm verdict needs ~100 matches, expected ~12 Nov if the logger runs. Date at risk: **PGL Major 25 Nov-13 Dec.**

### Tennis, NFL, NHL, cricket

**Tennis** (in-play $13.1M/day, the biggest single in-play pool after NBA/LoL/CS2; rn1 3.6-6.7%)
- Feed (measured): Cito (point-by-point) arrives a median 26-28 s after the price; Polymarket stream snapshots trail the price by a median 37 s. The point model is right (corr 0.74, beta ~1.0).
- Result (sim): even with a perfect zero-delay feed ~$2/match (~$120/day at 61 matches), up to $4 at a 120 s bid (~$260/day), an upper bound with oracle side and no queue. By 5 s after the price it is ~$0. The limit is fills, not the feed: sellers almost never print 2.5% under the market on the rising side (placebo gets 10-15x more fills).
- Bookmakers (queue-aware, 53 paired matches): Pinnacle ~$0/match (-0.15 to +0.06). bet365 $6.65/match, 90% -12.9 to +28.5, -$9.2 without the top 5. No edge. Pinnacle leads the price ~2.4 s, bet365 ~0.8 s.
- Status: no live trial. Next: none worth the spend unless a feed gets ahead of the price. Do not say "stays out".

**NFL** (in-play $5.6M/day, rn1 1.9%)
- Feed (measured, JAX@BAL, 21 moves): Polymarket stream every 5 min (4-8 min late); ESPN scoreboard 22.6 s and summary 32.2 s after the price; 8,400 shares queue ahead at 0 s.
- Result (sim, 119 games 2026): about $0/game at any feed we can buy; zero-delay upper bound ~$15/day. Only a feed 5-10 s BEFORE the price pays (~$80-140/day on 2026, weaker on 2025), which is courtside/official data (Genius, company-only). Closed as not planned.
- Next: the same capture can run on Sunday 8 Nov (13 games) if Nick wants a second queue sample.

**NHL** (in-play $0.5M/day) — PARKED (PR #139)
- Feed (measured, 14 goals): NHL api-web 50 s after the price, ESPN 64 s, Polymarket stream 95 s. 87% of the move done on arrival.
- Result (sim, 640 games): even a perfect feed is ~$4-5/game this season (~$35/day), $13-20 last season's test half (~$140/day). Official data is Sportradar, not worth it at this size.

**Cricket / BBL** (in-play $0.4M/day, rn1 0%)
- Feed (measured, 92 events 3 matches; 167 events 4 matches): ESPN ~30 s behind the price, 87% of the move done. Bookmakers: bet365 ~9 s AFTER the price, Pinnacle covers 4 of 26 matches, no lead. The earlier "15 s behind" was an artefact (placebo gave the same) and the $18.9/match bookmaker figure is noise.
- Result: delay curve inconclusive (1-10 fills per delay, one resolved match). Volume is tiny: WBBL ~$21k/game; BBL|16 might total $2-4M (estimate); IPL (Mar-May) is the one large cricket window.
- Faster feeds, untested: Decimal Data (Cricket Australia's exclusive betting partner), Goalserve (~1 s claimed, $125/month), Roanuz.
- Date at risk: **BBL starts 12 Dec** and needs a feed decision before then.

### Strategic builds, small today

**Rugby** (Six Nations $1.15M in 2026; ~$128k/match) — capability build, not profit. PM had no union moneylines in the test window. Top 14 capture windows: AB 7 Nov 13:15-18:05Z (6 matches), 8 Nov 13:45-16:30Z and 19:50-22:35Z. Six Nations Feb-Mar 2027 est. $1.2-2.5M volume; RWC 1 Oct-13 Nov 2027 est. $6-18M, $200-650 total at LoL yield.

**AFL** — listed on PM only from 8 Aug 2026; 36 men's games $126k total. Nick expects growth; model built offline before round 1 (17-21 Mar 2027).

**Valorant** ($0.23M/day, 72% in-play) — never assessed; rn1 zero fills.

## 4. Never assessed (no feed, no backtest)

| Sport | Why it matters | Status |
|---|---|---|
| **Soccer** ($19.2M/day in-play, 59%) | Largest in-play pool | Dropped on 3 Nov because rn1 is heavy there, not because it was shown infeasible. Plain rule lost ~8%/min in the sim (328 matches); rn1's real fills made +0.6%/1 min, so the sim is harsher than reality. Price jumps ~2 s before ESPN's goal time. Only revisit if Nick asks. |
| **MLB** ($0.9M/day) | Season over until spring | No work |
| **UFC** ($0.8M/day, 87% in-play) | Round/finish events | Untested (Cito feedback marked UFC untested) |
| **CFB** ($2.0M/day in-play) | Saturday volume; ESPN-fed like NFL | No work |
| **Valorant, WNBA, EuroLeague, CBA** | Small | No work |
| **Table tennis, volleyball, handball, snooker, badminton, darts, pickleball** | TheSports covers some; PM volume ~$0 in window; rn1 zero fills in table tennis, darts, pickleball | Check PM listing counts first; not assessed |

## 5. Ranked plan

Ranking is by evidence for an edge at an attainable feed, then by size, then by deadline.

### Now (to 14 Nov)
1. **NBA: verify.** Release the NBA capture; collect full-night 1 s books on 14 games; rerun queue and book-mid timing. This decides whether ~$70-145/day is real. Cost: nothing but server time.
2. **LoL: second dry sample tonight (T1 vs KC, 22:00Z), then decide on a faster feed.** The dry run says the free feed is 17.6 s late and bids land ~20 s late; 0 fills. Without a feed ahead of the price LoL is parked. Worlds final is 14 Nov, so a TheSports trial only pays off for LoL if it starts now.
3. **TheSports trial (LoL first, then Dota, CS2).** Ask them to start the 15 days after IP whitelist. Plan: ~10 days for LoL verdict, full 15 for Dota (BLAST 17 Nov) and CS2. Runs to ~21 Nov if started ~6 Nov.
4. **Dota: measure BLAST from 17 Nov** with whichever fast feed is on trial.
5. Rugby Top 14 captures 7-8 Nov; NFL second capture 8 Nov (optional).

### Next 3 months (mid Nov to Feb)
6. **CS2:** firm verdict ~12 Nov (100 matches); PGL Major 25 Nov at risk without a fast feed.
7. **Dota:** BLAST Slam 17-29 Nov, DreamLeague 2-13 Dec.
8. **Cricket/BBL:** decide Goalserve trial before 12 Dec; BBL 12 Dec-26 Jan.
9. **Rugby:** Six Nations model for Feb-Mar.
10. NHL parked; tennis and NFL closed unless a feed gets ahead of the price.

### 2027
11. LoL season from ~mid-Jan, MSI, Worlds; AFL 17 Mar-3 Oct; IPL Mar-May; Six Nations; Rugby World Cup 1 Oct-13 Nov.

## 6. Dates at risk

| Date | Item | Risk |
|---|---|---|
| 14 Nov | LoL Worlds final | Fast feed not tested; LoL dry run shows 0 fills |
| 17 Nov | BLAST Slam (Dota) | Valve feed 5-16 min late; needs a paid feed |
| 25 Nov | PGL Major (CS2) | Feed 15-20 s behind price; ~$0 per match |
| 12 Dec | BBL | Feed decision needed ~early Dec |
| 7-8 Nov | Top 14 capture | Starts only after gamma check on 6 Nov |

## 7. Decisions Nick needs to make

1. **TheSports trial: approve it (LoL first) or park LoL.** Quote $1,300/month for NFL/NBA/LoL/CS2/Dota ($200 each) and tennis ($300). They said 2-3 s typical, no ms timestamps. Recommendation: approve the free trial, LoL first, on the IP whitelist before the 15 days start. Decision cost is a trial only, but a live subscription follows only if the measured delay against the price is under ~5 s.
2. **Release the CS2, Dota and NBA captures** (paused since 5 Nov). NBA is the highest priority because its verification is the cheapest.
3. **Goalserve BBL trial** (~$125/month, ~1 s claimed): approve before early Dec, or drop cricket.
4. **NBA feed vendor:** say whether to pursue a sub-2 s NBA feed (Goalserve $250/month, Sportradar ~$10k/month) if the full-night books confirm the sim.
5. **Soccer:** confirm it stays dropped (default), since it is the largest in-play pool and never tested honestly.

## 8. Confidence: 6/10

- Factual accuracy of what is reported: about 8/10. Every figure comes from a repo note or project memory; I did not re-run any analysis, and I did not check Hermes or server status after 6 Nov 03:10Z.
- Mutually exclusive: yes by sport; some sports overlap in vendor (TheSports covers LoL, CS2, Dota).
- Collectively exhaustive: no, section 4 lists sports not assessed, and I could not check how many Polymarket markets exist for table tennis, snooker or badminton.
- To reach 9: (1) Hermes/agent status check for the 6 Nov events since 03:10Z; (2) full-night NBA books; (3) one live-fill sample in any sport; (4) a count of Polymarket markets for the unassessed minor sports; (5) TheSports measured latency against the price.

## 9. Re-prioritised list (6 Nov 07:10Z, Nick: rank by fast-feed value, feed availability, volume, date)
Headline caveats: every figure is sim; zero live fills anywhere (LoL dry run 0 of 62 bids); TheSports' 2-3 s is their claim, not measured against the price; LSports and Goalserve latency are vendor claims; project memory says LSports has no esports, so coverage there is unchecked. No $/day is given where the range spans zero. NBA stance unchanged: no proven edge until a sub-2 s feed exists.

1. LoL. Feed: TheSports ($200/mo). Sim clears zero at a 2-20 s lag (+$0.7k to +$20.5k over 531 games), spans zero at a fixed 20 s. In-play $10.2M/day. Next: approve trial now, measure vs price on Worlds semis 7-8 Nov and final 14 Nov. Tonight's T1 v KC dry run is the second sample.
2. Dota 2. Feed: TheSports. 1-min edge clears zero up to 30 s (+0.1 to +3.7%), spans zero at 60 s; the free Valve feed is 5-16 min late. In-play $5.8M/day. Next: measure on BLAST Slam from 17 Nov. Pinnacle route loses without its top 5.
3. NBA. Feed: none confirmed under 2 s. Sim clears zero only at 0-2 s (queue-safe, 429 games), spans zero from 5 s. TheSports claims 2-3 s generally (not NBA-specific); Goalserve NBA $250/mo is listed with no play-by-play latency. In-play $13.8M/day. Next: include NBA in the TheSports 3-day check and run the full-night books; ask Goalserve for a measured NBA latency.
4. Cricket / BBL. Feed: Goalserve (~$125/mo, ~1 s claimed). No verdict: delay curve inconclusive (one resolved match). In-play $0.4M/day. Next: Goalserve trial before 12 Dec, time it against the price first.
5. CS2. Feed: TheSports, bundled only. Even a feed 10-30 s earlier showed no edge (20 matches, ranges span zero). Next: 100-match verdict ~12 Nov. PGL Major 25 Nov.
Not prioritised: tennis (fill-limited, upper bound only at a feed before the price), NFL (needs a feed before the price), NHL (parked), rugby and AFL (capability builds), soccer/MLB/UFC/CFB/minor sports (unassessed).
