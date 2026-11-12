# TASK: Goalserve trial latency test (WAITING FOR KEY)

Status: ON HOLD until /etc/pkarbs/goalserve.env exists (GOALSERVE_KEY=...). Starts automatically then. Nick puts the key there himself; do not ask him to relay anything.

Test standard: feeds/STANDARD-feed-latency-test.md (v1). The benchmark is the Polymarket price, never another feed. Full plan: feeds/NOTE-goalserve-trial-plan-2026-11-12.md (project files). Do not change the pass rules after data.

## Part A: capture (chrony-synced clocks, data on /vol2 only)
1. Poll Goalserve live endpoints at 1 s (0.5 s if the vendor rate limit allows) for: cricket, LoL, CS2, Dota 2, tennis, NHL. Log per poll: local recv ns, HTTP Date header, payload sha1, parsed score/event fields, and first-seen time of every change.
2. In parallel record Polymarket CLOB trades + books for the matching markets (existing recorders), plus TheSports (live/thesports/capture.py), ESPN cricket and HLTV scorebot where they overlap.
3. Run through the whole 30-day trial. Log gaps, outages, stale polls.

## Part B: analysis (locked)
- Event = score change. Match to PM market by teams + start time; side by settlement, never by price co-movement.
- Lead = PM price-move onset minus Goalserve first-seen. Always report next to the random-time placebo on the same market, with n. Poll resolution +/-1 s stated.
- PASS per sport: STANDARD-feed-latency-test.md v1 section 3 (n>=30, median real minus placebo >= +2.0 s, bootstrap 95% CI by match excludes 0, PM price moves after the Goalserve message in >=60% of events). Benchmark = PM price.
- Side comparisons, information only, NOT pass conditions: Goalserve vs TheSports / ESPN / HLTV paired first-seen times (cricket: vs ESPN, which ties the PM price +0.5 s, n=48).
- Money bar if PASS: STANDARD section 5.
- Else: no lead, drop.

## Deadlines
- First capture the day the key arrives. LoL final 14 Nov only if key by 13 Nov.
- Cricket verdict by 5 Dec (BBL starts 12 Dec).
- Status in outbox/status every 30 min while blocked; if capture stalls, raise an IT issue immediately.
