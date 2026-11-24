# RN1 soccer, 35 days, per league, with competition (R-083, R-084, R-085). Pulled 24 Nov 2026 03:2x-03:5xZ from data-api v2. Paper/desk only.

## Method (and what it can't say)
- RN1 wallet 0x2005d16a84ceefa912d4e380cd32e7ff827875ea, `/v2/trades?user=..&taker_only=false` (all fills) and `taker_only=true` (taker fills). Maker fill = in the first set and not in the second (multiset difference on tx, token, size, price, side). Set difference, not on-chain.
- Window: fills from 20 Oct 01:47Z to 24 Nov 03:30Z (35.07 days; I stopped at 35 days, RN1's longer history is UNKNOWN). 312,938 fills, ALL BUYs; 151,531 are in soccer leagues (slug prefix is a soccer league per Gamma /sports tag 100350).
- Result: Gamma `/markets?condition_ids=..&closed=true`, every returned conditionId asserted to be in the request; a token's payout counts only if closed and price exactly 0 or 1. P&L = size x (payout - price), BEFORE rebates, held to result. Unresolved notional per league was 0 except Brazil ($16.6K).
- Valid-filter and wrong-param test: `test_wrongparam.py` (wallet=, user_address=, maker= return other wallets, the assertion in pull.py rejects them; PASS). `start`/`end` are never sent; the window is cut by timestamp. Competition pulls use `condition_id` and assert every row's condition_id equals the request.
- CI = game-cluster bootstrap of the notional-weighted return (4,000 resamples, seed 7). A game = one Gamma event, all its markets.

## 1. League totals (RN1 resting bids, maker fills; Ligue 1 and Serie A first)
| League | games | maker notional (resolved) | maker share of RN1 $ | P&L before rebates | weighted return [95% CI] | games with + P&L |
|---|---|---|---|---|---|---|
| Ligue 1 | 130 | $986K | 88.2% | +$54.5K | +5.53% [-3.28, +14.91] | 49% |
| Serie A | 196 | $2.97M | 94.6% | +$146.6K | +4.93% [+0.12, +10.23] | 52% |
| Premier League | 154 | $3.01M | 93.7% | -$77.2K | -2.56% [-6.07, +1.08] | 48% |
| LaLiga | 153 | $2.47M | 90.6% | +$19.6K | +0.79% [-3.52, +5.87] | 44% |
| Champions League | 136 | $2.88M | 91.6% | +$75.6K | +2.63% [-2.08, +7.25] | 52% |
| Bundesliga | 125 | $1.13M | 89.5% | +$6.6K | +0.59% [-5.69, +6.64] | 51% |
| Europa League | 127 | $1.39M | 92.2% | +$12.0K | +0.87% [-5.99, +7.15] | 58% |
| Nations League | 169 | $1.95M | 99.9% | -$12.2K | -0.62% [-5.99, +4.80] | 49% |
| Brazil | 179 | $0.81M | 99.2% | -$17.3K | -2.13% [-12.30, +8.04] | 52% |
Soccer volume shares of RN1 soccer $: EPL 10.6, UCL 10.4, Serie A 10.4, LaLiga 9.0, Nations League 6.5, Europa 5.0 (all >5%), Bundesliga 4.2, Ligue 1 3.7, Brazil 2.8.
Taker fills (not the strategy under test): Ligue 1 +6.3% on $8.3K, Serie A +7.4% on $12.7K resolved notional; tiny.

## 2. Reading it honestly
- Ligue 1 CI includes zero (-3.3% to +14.9%). Serie A CI just excludes zero (+0.1% to +10.2%) but it is concentrated: top 5 Serie A games = $123K of $147K P&L; ISO week 43 alone is +$106K (+19.0%), the other four weeks sum to +$40.6K on $2.4M (about +1.7%). Ligue 1: top 5 games +$70K of +$54.5K total (bottom 5 -$41.5K).
- Per-game return sd is 48% (Serie A) and 84% (Ligue 1): one game cannot tell. The unweighted mean per-game return is -0.6% (Serie A) and +1.6% (Ligue 1), t about -0.2 and +0.2.
- So: on 35 days RN1's Ligue 1 and Serie A book is NOT distinguishable from zero except marginally in Serie A, and Serie A's marginal result rests on one week. I cannot rank Ligue 1 against Serie A (CIs overlap almost fully): TOO SMALL TO RANK. Premier League is negative at the point estimate (CI includes 0).
- Per-game tables (match, date, maker resolved notional, fills, P&L before rebates, % return, plus unresolved and taker columns): `pergame_fl1.csv` (130 rows), `pergame_sea.csv` (196 rows).

## 3. Competition (taker_only=false minus taker_only=true on every condition RN1 traded in the two leagues, 1,746 conditions, 1.05M rows, no truncated pull)
| | Ligue 1 | Serie A |
|---|---|---|
| distinct maker wallets, league (35 d) | 2,743 | 4,477 |
| distinct maker wallets per game, median | 102 | 124 |
| makers with >= $1K notional in the game, median | 7 | 13.5 |
| makers with >= $5K in the game, median | 1 | 3 |
| RN1 share of maker notional, league | 7.1% | 8.2% |
| top-5 makers share of maker notional, league | 26.0% | 30.2% |
| top-5 share per game, median | 64.4% | 63.6% |
| maker notional all makers, 35 d | $13.8M | $36.3M |
| RN1 mean P&L per game | $420 | $748 |
| per material maker (>= $1K) | $31 | $33 |
| per big maker (>= $5K) | $105 | $102 |
Second-biggest maker (0x821dab) is larger than RN1 in Serie A ($3.24M vs $2.97M); in Ligue 1 it is nearly equal ($958K vs $986K). Many tiny wallets inflate "distinct makers", so the material-maker rows are the fairer comparison. By edge per competing maker the two leagues look the same ($31-33 per material maker, about $100 per big maker), with the same CI problem as section 2: the RN1 edge itself is not proven, so this is a ratio of an unproven number.

## 4. Depth: CLOB /book snapshots (SNAPSHOT, PREGAME, NOT in-play; recorder replaces them)
03:43-03:44Z (container clock) 24 Nov, each token's own book, upcoming games 27-30 Nov, n tokens/games below. No soccer match in these leagues is live today (Tuesday), so these are the next matches, 3-6 days before kickoff.
| League | tokens | games | median spread | median best-bid size (shares) | bid depth top 3 levels ($) | bid depth within 5c ($) |
|---|---|---|---|---|---|---|
| Ligue 1 | 54 | 9 | 0.020 | 820 | 1,449 | 2,709 |
| Serie A | 60 | 10 | 0.010 | 1,554 | 2,477 | 4,600 |
| Premier League | 66 | 11 | 0.010 | 2,133 | 4,239 | 6,297 |
| LaLiga | 66 | 11 | 0.010 | 2,564 | 2,745 | 4,695 |
Queue ahead at the best bid = the best-bid size (median row above). Pregame books are thinner than in-play books will be; do not read these as in-play depth. In-play depth needs the recorder (pm_sport_books.js epl|fl1|lal|sea, see the 12:00Z note).

## 5. What is and isn't established
- NOT established: that RN1's soccer maker book has a positive edge in Ligue 1 or Serie A (35 days, 130 and 196 games, one-week concentration). No $/day is claimed (R-034): RN1 P&L is RN1's own fills at RN1's sizes, not ours at $200 with measured queue.
- Established: RN1 is about 90% maker by $ in every soccer league listed; it is the second or largest single maker in Ligue 1 and Serie A, with 7-8% of maker notional; makers are concentrated (top 5 = 26-30%).
- Confidence 7/10 on the numbers as computed (data-api, resolution by Gamma closed prices, maker/taker by set difference, cross-check: RN1 maker notional in the competition pull equals the resolved maker notional in section 1 for Ligue 1, $986,455 each); 4/10 that this says anything about forward edge. To raise to 9: on-chain maker check on a sample, RN1 fills before 20 Oct, and in-play recorded books.
