# How Polymarket account RN1 makes money (29 Oct 2026)

Wallet `0x2005d16a84ceefa912d4e380cd32e7ff827875ea` (profile @rn1, X @RN1polymarket). Read-only, public data only.

**Verdict:** RN1 is not doing arbitrage in the sense this project tested (buying a complete set for under $1 at one moment). It is an **in-play sports market maker**: it rests bids on both outcomes of a game, gets filled by takers over minutes as the price moves, never sells, and holds everything to resolution. Its profit is spread captured on the two-sided part, minus losses on the one-sided leftover, plus maker/taker rebates and liquidity rewards. It carries real risk: 26% of days are losing days, and its largest drawdown was $281k.

## Sources and what each number is
- **Reported by Polymarket** (`data-api /v2/user-pnl`, `/v1/leaderboard`): lifetime and monthly P&L, fees, rebates, volume. These are Polymarket's own figures; I did not recompute them.
- **Measured by me from public fills** (`data-api /activity`, 21 Oct 02:00Z to 29 Oct 02:00Z, 81,369 rows) joined to gamma market results (99% of the dollars bought had resolved).
- **Estimated / inferred**: labelled where used.

## 1. Lifetime P&L, Jul 2025 to 29 Oct 2026 (reported)
| Component | $ |
|---|---|
| Trading P&L before fees | +14.80M |
| Net fees paid (gross 5.24M, of which 3.85M refunded) | -1.38M |
| Maker rebates | +1.18M |
| Taker rebates | +0.57M |
| Liquidity rewards | +0.33M |
| Yield and referrals | ~0 |
| **Total economic P&L** (includes +$18k unrealised) | **+15.50M** |

The leaderboard's $13.40M (rank 4 by P&L, rank 2 by volume) is realised trading P&L after fees, without the $2.08M of rebates and rewards. Volume was $692M in USDC terms across 5.07M fills. My reading of the $3.85M "fees refunded" is that it is the fee taken from maker fills and given back, which would fit a mostly-maker account (an inference, not documented).

## 2. Trajectory (reported, by month)
| Month | P&L $k | USDC volume $M | P&L / volume | Rebates + rewards share of P&L |
|---|---|---|---|---|
| Aug 2025 | 48 | 0.7 | 6.7% | 0% |
| Jan 2026 | 2,004 | 32.1 | 6.2% | 0% |
| Apr 2026 | 1,499 | 70.6 | 2.1% | 20% |
| Jul 2026 | 1,825 | 102.7 | 1.8% | 23% |
| Sep 2026 | 628 | 85.9 | 0.7% | 58% |
| Oct 2026 (to 29th) | 954 | 62.6 | 1.5% | 27% |

Volume grew about 100x while the margin per dollar fell from about 6% to 1 to 2%. Rebates and rewards began in March 2026 and are now a large part of the profit. Last 30 days: mean +$31.8k/day, median +$39.7k, standard deviation $47k, 7 losing days. Last 90 days: 31 losing days, worst day -$136k.

## 3. The last 7 days, measured (21 to 28 Oct)
**What it trades.** 72,749 fills, all buys. There were **0 sells, 0 merges, 0 splits and 0 negRisk conversions**, plus 8,595 redemptions. It bought $18.0M. The median fill was $37.5, the 90th percentile $642 and the largest $22.6k.

**When.** 93% of dollars were bought after the game had started. Pre-game: 7% at a +1.3% margin. First hour in play: 41% at +3.0%. 1 to 2 h: 40% at +1.0%. After 2 h: 13% at -0.6%.

**Where.**
- By sport: Counter-Strike 19% of dollars (+6.4%), tennis 24% (about +0.4%), and soccer across many leagues (Serie A +10%, EPL -4.6%, EFL -6.9%). Also NFL (-3.0%) and college football (+5.8%).
- By market type: moneyline 60% (+0.4%), totals 16% (+3.6%), child moneyline 11% (+5.7%), spreads 6% (-3.5%).

**Maker vs taker.** Over 83 hours, taker fills were **12.9% of dollars** (3,000 taker fills, $1.24M, against $9.61M of all fills). In a separate 5.8-hour window they were 3.7% of fills. So roughly 87% of its volume is resting orders filled by other people.

**Is it complete sets?** 90.5% of its dollars went into markets where it bought both outcomes. But only **3%** of dollars were filled within 5 s of a fill on the opposite outcome. 16% were within 5 to 60 s, 42% within 1 to 10 min, 24% within 10 to 60 min, and 15% after more than an hour or never. Its taker fills are not set completions either: only 3 of 111 had an opposite-side fill within 5 s. **The pairs build up over minutes as prices move. They are not locked at one moment.**

**P&L, MECE, before fees and rebates, on $17.8M of resolved buys:**
| Component | $ | Margin |
|---|---|---|
| Two-sided matched shares (min of the two sides in each market) | +435k on $11.07M | +3.9% |
|   of which markets where the average combined cost was under $1 | +884k | |
|   of which markets where the average combined cost was over $1 | -449k | |
| One-sided leftover shares | -139k on $6.75M | -2.1% |
| **Fill P&L** | **+296k** | **+1.66%** |
| Maker rebates + taker rebates + rewards paid in the window | +82k (41k + 25k + 15k) | |

This is consistent with the leaderboard's 7-day figure of +$360k after fees (the windows differ slightly). The signature is a market maker's: the round trip earns the spread, and the inventory left over loses money to adverse selection.

**Concentration.** 44.8% of markets were profitable. The top 1% of markets made +$942k and the bottom 1% lost -$754k. The biggest single result was -$51k (Hull v Brentford over/under 2.5). Over the lifetime, the biggest single-outcome wins and losses are $200k to $240k each, and they are usually the two sides of the same match. For example, in Alcaraz v Zverev (Australian Open) the Alcaraz side made +$243k at an average price of 0.37 and the Zverev side lost -$189k at 0.47, so the match netted +$54k. It is not a few lucky wins: the profit comes from thousands of markets, and the swings within each match are large.

## 4. What the FT says
The FT piece (28 Oct, "Polymarket's top trader is sports gambler 'Swiss Tony'", paywalled) is about the account **swisstony**: $12M over six months, about 184k trades, less than 2% average return, up to $17M deployed at once. According to Bloomingbit's summary, the FT mentions RN1 only in passing, as an account that "placed buy orders on both sides of outcomes and sought profit opportunities from price gaps", effectively "a market maker supplying liquidity". The data above agrees with that description. I could not read the FT text itself.

## 5. Against the project's earlier conclusions
| Earlier verdict | Contradicted? | Why |
|---|---|---|
| Cross-venue locked pairs (PM vs Kalshi) cost $1.02 to $1.04 after fees | **No** | RN1 trades Polymarket only and does not lock pairs. |
| In-play negRisk set arb loses as a taker at 1 s delay (12 h, -$404) | **No** | RN1 is about 87% maker. Its taker fills are not set completions. |
| Macro release pickoffs are lumpy, $10-25/day add-on | **No** | Not related. RN1 trades sports only. |
| Rebates matter (24 Oct) | **Confirmed** | $2.08M lifetime, and 58% of September's P&L. Its taker rebate is about 41% of fees, which means near the top tier. |
| Maker side of in-play sports closed as negative (25 Oct: average maker markout about 0 in quiet play, -2.4c near goals; $50/day would need 3-8% of all in-play maker volume with near-perfect cancels) | **Yes, partly** | That bound described the average maker over a 60 s horizon in soccer. RN1 shows that a top maker, across CS2, tennis and soccer and holding to resolution, earns about 1.7% of volume before fees and roughly $30k/day. We closed the maker line on an average, and RN1 is a counter-example at the top of the distribution. It does not show that a new entrant would be above average. |

So "arbitrage doesn't work" still holds for riskless locked arbitrage. "Market making doesn't work" was too broad a conclusion from our 60 s markout test.

## 6. What it would take (estimates, not measured)
- **Edge source (inferred):** prices that are better than the crowd's in play (a sharp odds or model feed), quoting both sides, and fast cancels around goals, points and rounds. Profit is highest in the first in-play hour, and above-1 combined costs in a market (-$449k/week) are what bad quotes cost.
- **Scale:** about $2.5M of fills a day. For Nick's $50/day at RN1's recent ~1.5% all-in margin, about $3.3k/day of fills would be enough. But an average maker earns about 0 by our 25 Oct measurement, so the margin depends on skill, not just size.
- **Cheapest next test (read-only):** replay RN1's own public fills in one sport against a reference price (for example, the mid one minute later, or Pinnacle closing odds) to see where its edge comes from: pricing versus spread versus rebates. Then decide whether a paper maker in one niche (CS2 or tennis) is worth building.

## Confidence: 7/10
- Solid: the lifetime and monthly figures (Polymarket's own P&L endpoint), and the 7-day all-buys / no-merge / hold-to-resolution pattern and P&L decomposition (computed from 72.7k fills, 99% resolved).
- Weaker: the maker share (two windows of 5.8 h and 83 h from the `takerOnly` flag; the on-chain subgraph was rate-limited), what "fees refunded" means, and the FT wording (summary only).
- To reach 9: (1) maker/taker for every fill from the on-chain order-filled events over the full 7 days, (2) the FT article text, (3) a check of whether RN1 runs other wallets. FT analysts suggested that profitable traders split accounts.

## Method notes
- Data was pulled in the Composio sandbox, because the container proxy blocks Polymarket. Activity was paged in 1-hour windows with recursive splitting.
- "Matched" means, per market, min(shares of outcome 0, shares of outcome 1) at each side's average price. The leftover is the excess on one side.
- Fill P&L = shares x payout - USDC paid. This excludes fees, so it is pre-fee.
- Timing uses gamma `gameStartTime`.
