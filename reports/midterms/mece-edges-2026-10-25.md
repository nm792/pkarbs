# MECE edges in newer markets and the US midterms (25 Oct 2026)

Desk research only. No server use, no orders, no new scan job. One snapshot of live books (Polymarket clob/gamma and Kalshi trade API, read through TinyFish between 11:46Z and 12:05Z on 25 Oct), plus about three weeks of hourly price history from both venues. Raw data and scripts are in `data/midterms-2026-10-25/` and `scripts/midterms/`.

Labels: **measured** = computed from a fetched book or history; **estimated** = needs an assumption, which is stated.

## Bottom line

1. The only pool worth anything is **Senate control across venues**: Kalshi "Democrats win Senate" is cheap compared with Polymarket. At the snapshot, buying Kalshi D YES at 0.63 and Polymarket "Republican Senate" (directly, or more cheaply through Polymarket's Senate × oil combo markets) cleared **about $2,100 measured, on about $102,000 of capital**, after the Kalshi taker fee. That is roughly a 2% return over ~10 days to election night, plus however long resolution takes. Polymarket charges no fee on these markets.
2. Across five matched race pairs (Senate and governor), cross-venue gaps at the snapshot add up to **about $400 measured**.
3. Every single-venue negRisk set I checked is worth between $0.05 and $2.31, so I would close that category.
4. **Against the $50/day target**, this is a one-off of about $2,500 before 3 Nov, and it needs about $100k of capital spread over two venues. It does not repeat after the election. The history suggests the cross-venue gap reopens in about 20% of hours, at about 0.45c net when open (estimated). That is too thin to make a recurring $50/day on any capital we are likely to commit.

**Confidence 6/10.** What would raise it to 9 is in the last section.

## Categories (MECE)

The categories are split by **where the legs trade** (one venue or two) and **how the legs relate** (a partition of one event, a sum across events, or a nested or threshold link).

| # | Category | Example checked | Snapshot pool (measured) | Verdict |
|---|---|---|---|---|
| A | One venue, one event: buy all YES of a negRisk set | PA-08, AL-03, CA-12, NE-02 House races; Hormuz × Senate 3-way | $0.05, $2.31, $0.58, $1.30; Hormuz about $0.40 (10-30 shares at the gap) | Close |
| B | One venue, across events: the same outcome built two ways | Polymarket "R Senate" built from Senate × oil combos vs the main Senate market | $62 for 16.5k sets (at 0.7c), cover includes "Other" | Small, persistent, feeds C |
| C | Two venues, same outcome | Kalshi CONTROLS-2026-D vs Polymarket Senate R (main or synthetic) | about $2,109 on $101.8k (first Kalshi tier); $2,637 on $241k for the full walk | **Worth a bounded test** |
| D | Two venues, individual races | Maine (Collins), Michigan (El-Sayed), Minnesota (Tafoya), TX governor (Hinojosa), NH (Sununu) | about $200 + $122 + $74 + $11 + $5, so about $400 | Fold into C's test |
| E | Nested or threshold (seat brackets vs control, combos vs marginals) | Polymarket R seat brackets (ask sum 1.102), Kalshi D seat brackets (ask sum 1.071), Kalshi balance of power vs Kalshi Senate | No buy-side arb. Balance-of-power vs Senate on Kalshi costs 1.021 after fees | Close |
| F | Time ladders (by-date nesting) | "Hormuz agreement by 23 Oct" vs "before midterms" | 23 Oct has passed; the dated legs trade at 0.001 | Nothing open now |

### A. Single-venue negRisk sets (close)
- Of the 196 midterm negRisk events I scanned (the first 200 of the midterms tag), the lowest gamma ask sums are 0.99 to 0.999. All of them are one tick on two-candidate races. Walking the actual books (measured) gives $0.05 (PA-08), $2.31 (AL-03), $0.58 (CA-12) and $1.30 (NE-02).
- **Kill mechanism:** depth. The top level is 5 to 40 shares. There is also an uncovered "Other" placeholder: these events are augmented negRisk, so buying both named candidates does not pay if a third person wins.
- Two traps in the gamma screen. Some "two-leg" events have only one live candidate, with the second leg being a placeholder (AL-04 at 0.989). And the Hormuz 3-way shows 0.987 on gamma but has 10 to 30 shares at those prices.

### B. Polymarket synthetic Senate control (small, persistent)
- Polymarket lists at least five events that each split Senate control (main market, balance of power, Senate × oil <$80, Senate × oil <$85, Senate × Hormuz+oil). Summing the oil legs builds "R Senate" at 0.323 against 0.34 in the main market (measured snapshot).
- In hourly price history since the combos listed on 12 Oct, the main R price minus the synthetic R price averages **+0.8c (oil 80) and +2.2c (oil 85)**, with the last 10 hours at +1.6 to 1.8c (measured on last-trade/mid prices, not asks).
- On one venue, buying synthetic R plus main "D YES" or "R NO" clears $62 at the snapshot (measured). Using "R NO" also covers the "Other" outcome.
- **Kill mechanisms:** the oil leg is a true partition (< vs ≥), so oil does not matter. The Senate wording in the combos matches the main market (both cite "control of the United States Senate", and the main market uses the VP tie-break). Leftover risk is the combos' own UMA resolution.

### C. Kalshi vs Polymarket Senate control (the one to test)
- **Snapshot (measured, 11:52Z):** Kalshi CONTROLS-2026-D YES ask 0.63 with 105,674 contracts (NO bid 0.37), and Kalshi R YES ask 0.37. Polymarket main D is 0.66/0.67 and main R is 0.33/0.34 (31.6k at 0.34, 723k at 0.35). Fee per pair: Kalshi 0.07·p·(1−p) = 1.63c at p=0.63; Polymarket political markets have `feeSchedule.rate = 0`.
  - Main Polymarket R only: 105.7k pairs, **$895** net on $103k.
  - Using Polymarket's cheaper synthetic R as well (category B): **$2,109** net on $101.8k, at pair cost 0.969 to 0.986.
- Kalshi's own balance-of-power market implies D Senate at 0.656 (DD 0.65 + RD 0.006). So the Kalshi CONTROLS-D contract is cheap even against Kalshi itself.
- **Persistence (estimated from 465 hourly closes, 4-25 Oct):** Polymarket D mid minus Kalshi D ask averages 1.0c (range −1.5c to +3.5c). Assuming the Polymarket R ask equals its mid plus 0.5c, the main-market pair is profitable after fees in **93 of 465 hours (20%)**, with a mean edge of 0.45c when open and a maximum of 1.37c. Today's 3.5c gap is at the top of that range: Kalshi D fell from 0.65 to 0.63 overnight while Polymarket stayed put.
- **Kill mechanisms, tested or stated:**
  1. *Stale quotes:* not the issue. The Kalshi level is a 105k resting order, and the Polymarket clob and gamma agree within 33 s. The real risk is that the gap closes before both legs fill. The legs are deep, the markets are slow, and there is no sports-style matching delay, but this has not been tested with a live order.
  2. *Resolution basis:* Kalshi resolves on the party of the President pro tempore on **1 Feb 2027**, or early if 4 of 8 named media desks call control. Polymarket resolves on the majority of seats as elected (independents counted by caucus, VP breaks a 50-50 tie, then the President pro tempore). They differ only in tail cases: a party switch between election and 1 Feb, a 49-50-1 Senate with an independent who refuses to caucus (Osborn in Nebraska trades about 25% on Polymarket), or a media call later reversed. A divergence is all-or-nothing on both legs, so even a 0.5% chance costs as much as a quarter of the edge. **Estimate: under 1%, but not zero.**
  3. *Fees:* included. The Kalshi fee rounds up per order. The Kalshi contract terms PDF says orders come in "multiples of 5,000 contracts". That reads like a stale template line, but it should be checked in the UI.
  4. *Capital and time:* about $1 locked per pair until both venues settle. Kalshi can settle early on media calls; Polymarket goes through a UMA proposal and challenge window. Holding rewards (4% a year on the Polymarket main Senate market, `holdingRewardsEnabled`) and the interest Kalshi pays (assumed about 4%, as in the 20 Oct notes, not re-checked) roughly cancel the carry.
  5. *Position limits:* $125k per individual on Kalshi. Not binding at this size.

### D. Race-level cross-venue (fold into C)
- Snapshot books (measured; Kalshi NO = 1 − YES bid; fee included):
  - Maine Collins: Polymarket YES 0.36 + Kalshi NO 0.61 = 0.987 for 12.2k, then 0.997 for 11.6k, about $200.
  - Michigan El-Sayed: Kalshi YES 0.69 + Polymarket NO 0.29 = 0.995 for 24.5k, about $122.
  - Minnesota Tafoya: 0.990 for 7.3k, about $74.
  - TX governor Hinojosa: about $11. NH Sununu: about $5.
- Maine's history (466 hours, estimated the same way as C): profitable in 54 hours (12%), mean 0.49c when open.
- **Basis:** Kalshi race markets pay on who is *sworn in* for the 2027 term (or early on media calls). Polymarket pays on who wins the election. They diverge if the winner dies or withdraws before swearing-in. Small but real.

### E/F. Nested, thresholds and time ladders (close)
- Seat brackets are overpriced on both venues (Polymarket R ask sum 1.102, Kalshi D 1.071). Through negRisk conversion, Polymarket brackets ≥50 come to the same price as main R at 0.34, so there is no gap.
- Polymarket House: D 0.91/0.92 vs Kalshi D 0.906/0.907. Both cross pairs cost ≥0.997 before fees. Closed.
- Kalshi balance-of-power "Republicans sweep" (0.094/0.095) vs Polymarket (0.07/0.08): Polymarket YES 0.08 + Kalshi NO 0.906 + fee is about 0.992 at top of book. Kalshi depth was not fetched, so this is unverified.
- **New market types:** the Polymarket Senate × oil and Senate × Hormuz combos (listed 12 Oct, $0.2-1.6M volume, fee 0) are where the systematic mispricing sits (B). Kalshi Combos (parlays) are sports-first and were not checked.

## Sizing against $50/day
- Before 3 Nov there are about 9 trading days. $50/day is $450.
- The snapshot pool (C+D, about $2.5k measured) is larger than that, but only with **about $100k deployed across both venues**, and it is paid once.
- After resolution the midterm pool is gone. A recurring version would mean (a) re-entering whenever the gap reopens (20% of hours, about 0.45c) and (b) selling the pair back when the gap inverts. That is unmeasured. At 0.45c on even $50k turned over weekly, it would be about $30/day (estimated, optimistic).

## Recommendation
- **Worth a bounded test:** C and D together, as one logging task. Nothing is traded until you approve.
  - What runs: one process polls about 30 matched pairs every 60 s for 48 h. That is about 3 MB/h of top-5 levels with 50 MB RSS, so it runs on the container or a laptop, not the shared server.
  - Data per pair: depth to $5k on both legs, each venue's server timestamp, and the net edge after the Kalshi fee.
  - **Pass (fixed now):** at least one pair shows net edge ≥ 0.5c with ≥ $5k on both legs, held for ≥ 15 consecutive minutes, in ≥ 10% of the 48 h.
  - **Fail:** below that, and we close the category.
  - If it passes, the next step is one live $50 pair trade per venue to measure fill and slippage. That needs funded accounts on both venues and your go-ahead.
- **Close:** A, E, F.
- **Separately (not tested):** election night itself (3-4 Nov) will produce fast cross-venue moves as results come in. That is the same latency game that just lost money in sports, so I would only log it, not trade it.

## Confidence and what would raise it to 9
**6/10.** The snapshot numbers are measured. Persistence rests on hourly closes (not tick-level asks), the basis-risk probability is my estimate, and only about 200 of about 1,250 Polymarket midterm events and about 30 Kalshi series were scanned.

To reach 9:
1. The 48 h log above, which measures how often and how long the gap stays open at real ask depth.
2. Kalshi's full rulebook section on "accelerated determination" and a direct check of the 5,000-contract order line.
3. A full scan of the remaining about 1,050 Polymarket midterm events (about 11 more page fetches) and the Kalshi governor/House series.
4. One live small pair trade to confirm fills on both legs.
