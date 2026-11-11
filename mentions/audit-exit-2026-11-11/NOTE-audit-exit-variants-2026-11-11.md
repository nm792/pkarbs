# Independent audit: exit variants for the frozen Polymarket 10c entry (11 Nov 2026)

**Verdict: numbers REPRODUCE, but the "1h / 6h / 24h time exits" are not time exits. Realistic exits do no better than holding. PASS only in the sense "does not break the hold result"; no exit is better than hold. Confidence 7/10.**

Rebuilt from raw Polymarket trades: full trade history (taker trades only, `takerOnly` is the API default, 1,088,774 trades, 17,438 markets, `pull2.py`) for the 909 post-burn events; causal base rates; entry 10c, first hour. Code `exitaudit.py`, `ex2.py`, `ex3.py`, full output `exit_audit_output.txt`.

## 1. Reproduction (causal entry, same-side placebo at the bet's own size)
| Variant | P&L (hold: +$2,342 on $2,970) | Paired t vs placebo | Later half t |
|---|---|---|---|
| V1 first SELL print at/after entry+1h, uncapped | +$1,849 | 4.62 | 3.91 |
| V2 same, +6h | +$2,004 | 4.58 | 4.02 |
| V3 same, +24h | +$1,993 | 4.19 | 3.20 |
| V1 / V2 / V3, capped by sell-print size (rest held) | +$2,233 / +$2,322 / +$2,150 | 4.72 / 4.78 / 4.41 | 3.83 / 4.16 / 3.46 |
The build thread's figures (+$1,932 / +$2,063 / +$2,119; capped +$2,283 / +$2,356 / +$2,234; t 4.5-4.9) match within the difference between their start-ordered and my causal entry set. Placebo checked: the code gives every first-hour BUY print of the same event the same exit rule, so the placebo does use the same exit.

## 2. What the "1h/6h/24h" exit actually is (the main finding)
The rule sells at "the first SELL print at or after entry+h", with no limit on how late that print is. For the 285 actual bets:
- Only **1%** have such a print within 15 minutes of the planned time and **7%** within an hour (V1). Median delay after the planned time is **10.7 h** (V2 10.1 h, V3 12.9 h); 90th percentile 87 h. Total median hold before the sale: **11.7 h / 16.1 h / 36.9 h**.
- 28% (V1), 37% (V2) and 58% (V3) of bets have no later SELL print at all and are simply held.
- So V1, V2 and V3 are almost the same rule ("sell when some taker next sells, usually the next day"), not three different exit times. The time label is misleading, and the sale price is a future print that could not be known at the planned exit time.
- Bound the delay and nothing changes: requiring the sell print within 15 min (or 60 min) of the planned time gives +$2,351 / +$2,357 / +$2,367 versus hold +$2,342, i.e. the exit almost never triggers. A backward-looking version (last SELL print in the 15 minutes before the planned time, size-capped) is +$2,341.

## 3. Do exits beat holding? No
- First SELL print: costs about $494 (V1), $339 (V2), $350 (V3) versus hold; mean exit price is 4-9c per share below the resolution payoff. Win rate rises (188 vs 161 of 285) but average profit falls.
- Second SELL print after the planned time (a latency-realistic price once the first print is seen): V1 +$2,378, V2 +$2,385, i.e. equal to hold (t 4.7-4.9). So the lower P&L of the first-print version comes from the first print being unrepresentatively low (thin bid), not from a real exit cost, and no exit adds P&L.
- The paired t of 4.6-4.9 versus 4.6 for hold is not extra evidence: same entries, same placebo base. Bonferroni x5 across exits is fine; with the entry's own 12 variants (see earlier audit) x16-x40 it still passes (t 4.6 gives p of about 4e-6). The exit family does not change the entry verdict.

## 4. Your specific checks
- **Exit fill not capped by print size:** confirmed in `pm_exit_bt.py`. Only 46% of exit prints are at least our size (median ratio 0.82-0.95). The capped file's rule (remainder held to resolution) is reasonable and I reproduce it (t 4.4-4.8, later half 3.5-4.2). Cost of the cap about $90-$180 per variant.
- **SELL-print realism:** the trades API default is taker-only, so a SELL print is a taker hitting a bid at that price and size, so selling there is executable only if you act at that moment. Selling at the first print after an unbounded wait is not the same as hitting the bid at the planned time; the second-print and bounded versions in section 2-3 are the more honest bounds (about equal to hold).
- **Entry/exit ordering:** all exit prints are strictly after the entry print and at or after the planned time; none after the market's close (0%). Same-second ties are immaterial.
- **Placebo:** same exit rule on every first-hour BUY print; same-side and any-side placebo both pass (V3 later half is the weakest at t 3.2-3.3).
- **V4 limit sell at base-rate probability:** their fill (later BUY print at or above the target, no size cap) gives +$1,098 (t 2.9, Bonferroni x5 0.02, later half 3.0). A strict version (buy print strictly above target, size capped, 60 s after entry) gives +$1,718 (t 3.4, later half 3.1). Both are below hold: selling at our own probability gives up the upside on winners. The queue-ignoring assumption is not what makes V4 look good; V4 is simply worse than holding.

## 5. Conclusion for the strategy
Holding to resolution remains the best-supported rule. A bot watching the tape could sell into later bids without losing much (about equal to hold), but no exit variant improves P&L, and the "time exit" description should read "sell into the first taker sell after the planned time, median about 11 h later". Capacity is limited by first-hour qualifying entry size (about $12.8k of qualifying prints over 477 days), not by exits.

## Confidence
7/10. Reproduced from raw trades; open points: historical order books are not available, so the executable bid at any planned exit time is unverified; and all results rest on the same 285 entries.
