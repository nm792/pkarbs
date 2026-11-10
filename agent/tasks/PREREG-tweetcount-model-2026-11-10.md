# PRE-REGISTRATION: Elon tweet-count live-count model (written 10 Nov 2026 ~04:40Z, before any paper trade)

Rule, fixed now, not to be changed on the same data:
- Windows: every 'Elon Musk # tweets <start> - <end>' event, 7-day and 2-day.
- Decision times: 24 h, 12 h and 6 h before the window end (tracker end time, 17:00Z or 16:00Z).
- Model: final = xtracker count so far + expected remaining. Expected remaining = sum over the remaining hours of the average posts per UTC hour-of-day over the previous 21 days (from xtracker post timestamps). Spread: normal, sd = max(k x remaining, sqrt(remaining)) with k = 0.44 at 24 h, 0.65 at 12 h, 1.0 at 6 h (fitted on the closed-market history in forecast-edges/NOTE-late-pricing-opportunities-2026-11-10.md). Bracket probability = normal mass over [lo-0.5, hi+0.5].
- Paper trade: at each decision time, for each bracket with ask in (0.02, 0.98): BUY YES if model probability - ask > 0.05 (price paid = best ask, size = min(depth at best ask, $25)); BUY NO if best bid - model probability > 0.05 (price paid = 1 - best bid, same size rule). Hold to resolution. At most one decision per bracket per time.
- Judge once, after 8 weekly windows (about 8 weeks) or 30 2-day windows, whichever is later. Pass: net paper P&L positive and ROI on stake above 10%, with the sum of per-window P&L positive in at least 60% of windows. Fail otherwise. No re-picking thresholds on the same data.
- Inputs recorded by agent/tasks/tweetcount-recorder.py (xtracker total and book every 5 min, per window).
Label: all P&L is paper, computed offline on recorded asks. Nothing here is a live order.
