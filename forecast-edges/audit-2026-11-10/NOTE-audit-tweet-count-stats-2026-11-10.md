# Audit of the tweet-count backtest statistics (10 Nov 2026)
Rebuilt independently from raw data: Polymarket gamma (events), data-api /v2/trades (real prints), xtracker posts via TinyFish. Scripts in this folder (an.py = 24h/12h/6h run, start_an.py = window-start run on real fills, early_an.py = early last-trade claim). Raw pulls not copied (67 MB + 5.5M trades); fetch.py/fetch2.py regenerate them.

## What stands
- Count source: my post counts land inside the winning bracket in 99 of 100 Elon weekly windows.
- Rebuild of the Elon-only 24h run (their rule, 100 windows): +$809 on $1,390, t=1.78 (theirs: +$842, t=1.81). Their code and numbers reproduce.
- No look-ahead in model inputs (profile uses posts before the decision time). Train/test leakage is minor (k, b fitted on the first half, the first half is then scored in-sample, which only flatters the train rows).

## What was wrong or overstated
1. Hindsight fill choice: the run takes the max-edge print out of the next 10 minutes (the cheapest print in hindsight). A causal rule (first qualifying print) gives +$872 but t=0.87, 95% bootstrap CI -$529 to +$3,271.
2. Profit is five bets. Top 5 bets = $782 of $809. Drop the top 3: +$157. Median bet is $6 (stake, not profit). Cap each bet at $50: +$361 and a matched placebo earns $647.
3. Placebo too weak. Theirs draws any BUY print in the window. A placebo matched on side and price (+-10c) earns $611 +-508 against real $809: z=+0.39 (theirs +0.7). The pool of all BUY prints earns +4.5% on its own (side Yes +8.9%, No +1.8%), so the "edge" is mostly that baseline.
4. Horizon picked after the fact: 24h +58%, 12h -28% (-$674 on $2,405), 6h -6%. Only one of three horizons is positive, and it is the one reported.
5. Test half: 24h +25% on $405 (+$103, t=0.92, CI -$101 to +$342); 12h -22%; 6h +28%.
6. Their t and "SD" are fine arithmetically but ignore the number of variants tried (3 horizons x 2 thresholds x 2 window lengths x pick rules, plus 6 variants before that). At that count a t of 1.8 is expected by chance.
7. Pooled 454-window figure (+50%, t=2.07, 0.9 SD) is 84% Elon plus accounts with $24-$262 stakes; the six other accounts contribute $301 in total.

## Early "significant" claim (+10% on last trade, t about 2.4)
Reproduced on last-trade price at window start: ROI +8.3%, per-bet t=3.15 over 115 bets in 47 events (test half t=2.19 per-bet, 1.90 clustered by event). Prices were stale by about 1h, not by days, so staleness was not the cause. The t treated bets as independent although several brackets of one event are bet together; clustered by event it is lower in the test half. More important: the same rule on real BUY prints at window start (97 windows) gives train +18% / test -2% (first-print +22% / +1%), z -0.4 against a matched placebo. So the signal was in last-trade prices only and did not survive real prices; the claim of significance was never valid for trading.

## Verdict
No proven edge in Elon or the other accounts. Confidence 8/10 in that verdict (I reproduced their numbers independently and the conclusions are the same under four fill rules). Not covered: Trump (count source wrong), 2-day windows, other horizons or thresholds.

## Placebo check (08:15Z, requested by coordinator)
placebo2.py: oracle that knows the winner scores +11.5 SD against the same-event matched placebo, so that placebo discriminates (unlike the Netflix one). Random picks from OTHER events, matched on side and price: real +$809 vs $178 ± $1,105, z +0.57 (same-event: $639 ± $501, z +0.34). Verdict unchanged.
