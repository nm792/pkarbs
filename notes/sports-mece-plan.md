# Sports MECE in-play arbs: shadow test plan (23 Oct 2026)

Source: handoff brief from the temperature project (22 Oct sampler, 11:39-20:50Z). The underlying files
(LIVE-SPORTS.md, livesports.py, live_analyze.py, live_results.txt, README.md) are NOT yet in this project.

## Where the data stands
- 129 sub-$1 runs across 37 in-play negRisk matches, $325.84 net of fees at first sight; 12 runs still open
  after 3 s worth $162.38, mostly one match (Juventus v Rennes). One day, one sport, polled every ~2 s.
- Upper bound only. Unchecked: real fills, leg risk, maker behaviour during the sports taker delay, other days.

## Reconciling with the 22 Oct Nautilus verdict
- That verdict (7/10) said: log books first, revisit Nautilus only if fee-beating crossings appear and vanish
  within seconds. The 22 Oct sampler is that log, and it shows exactly that, so the condition to revisit is met.
- What changes: this strategy is single-venue (Polymarket only), so the Kalshi leg and transatlantic latency
  from the verdict no longer apply. Hosting near the PM CLOB (AWS eu-west-2, London) is what matters.
- What does not change: the binding constraint is Polymarket's sports/game delay, not our latency.
  Per PM docs, marketable orders on configured sports markets wait the market's delay window before matching
  and cannot be cancelled while held; risk checks re-run at expiry. The delay exists to protect makers from
  stale post-goal quotes, which is the exact edge here. Expect makers to cancel inside the window.
  So the test question is: what fraction of gaps survive (our RTT + delay D), on every leg at once?

## Phase 0: access and hosting (blocker)
- This project's container: Polymarket and Kalshi APIs return proxy 403.
- Composio remote sandbox: clob, gamma and Kalshi all return 200 (~0.05-0.2 s), but it has a 3-minute
  command limit, so it can do spot checks only, not multi-day logging or Nautilus.
- Multi-day shadow needs an always-on host: the shared one-wallet/one-node box from the brief, ideally a
  London VPS. Need: where that node runs and whether this project can reach it.

## Phase 1: measure the delay (read-only, cheap)
- For each in-play negRisk match, read GET clob.polymarket.com/clob-markets/{condition_id} at kickoff,
  every few minutes in play, and after full time. Record any delay/seconds fields and when they switch on.
- Output: D per market (replaces the unconfirmed 1 s / 3 s).

## Phase 2: Nautilus round trip (the MFW 10-order speed test)
- Shadow-safe variant (no fill risk): post-only limit orders priced far from the touch on a liquid market,
  then cancel. Measures sign -> ack -> book-visible -> cancel-ack. 10 orders, tiny size.
- These are still real orders on the wallet, so they run only with Nick's explicit go-ahead.
- Not testable without fills: how the delay window behaves for a marketable order. Phase 3 models that.
- Need from Nick: the MFW test script/results, and where the Nautilus node lives.

## Phase 3: multi-day shadow sampling (no orders)
- Nautilus (or livesports.py) subscribes to WebSocket books for every leg of every in-play non-augmented
  negRisk match. Log full top-of-book plus depth to the needed size, with exchange and local timestamps.
- On each detection (sum of leg asks + fees < 1 at size S), simulate:
  - submit at t0 + measured RTT (Phase 2); match at t0 + RTT + D (Phase 1, plus D = 1 s and 3 s variants);
  - each leg fills only if its ask at match time is <= our limit with enough depth;
  - partial fills: unwind filled legs at the bid at match time, charge fees, record the loss.
- Run at least 7 consecutive days including a full weekend of European football; add other sports if live.
- Report per day: detected $, survival-adjusted $, leg-risk losses (mean, worst), gap survival curve vs
  seconds, depth at the gap, concentration (share of $ from the top match).

## Go / no-go for any live trading
- Go only if the shadow result, after leg-risk losses, clears the project bar (~$50/day) across most days,
  is not driven by one or two matches, and the worst single leg-risk loss is small relative to bankroll.
- Prior (my guess, not measured): survival-adjusted value will be well below the $162/day ≥3 s figure,
  because makers can cancel during the delay and one match drove most of it.
