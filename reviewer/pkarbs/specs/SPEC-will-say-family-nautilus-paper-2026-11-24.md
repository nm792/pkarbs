# SPEC v1 (24 Nov 2026): "Will X say Y" family, Nautilus-native live paper node. Written by the Reviewer (R-076 due 14:00Z; the owner thread did not deliver)

Paper only, no orders ever (SETTLED A6/A7). STATUS: SPEC ONLY. Nothing here is built for Nautilus. The existing recorder P121 (it/mentions_pm_ws_paper.py at 075452ecd5, health PASS 10:23Z) is the evidence feed, not the paper node. Earnings-beat ("will X beat EPS/revenue") is EXCLUDED: it is a different contract with its own spec (R-087, due 25 Nov 14:00Z).

## 0. Scope: one family, every "will X say Y" market (Nick 24 Nov 02:50Z, repeated x3)
- One family: every Polymarket event tagged mention-markets, plus any "will X say Y" market without the tag. Live read 14:07Z: 11 open events and 132 markets. Sub-types include earnings-call mentions (Dell 24 Nov, Deere 25 Nov, Salesforce 2 Dec), Trump/White House remarks (pardon 24 Nov, November, APEC, Philippines), keynotes (Jensen Huang GTC DC), streamers (Caedrel) and sports announcers.
- Sub-types are CELLS of one family, judged separately (no pooled averages), sharing one rule.

## 1. Known facts (each cited; each must hold or the node does not start)
| # | Fact | Source |
|---|---|---|
| F1 | Each token is its own book; price from its own asks only; NO never derived from YES | SETTLED A1 |
| F2 | Fee: feeType mentions_fees, feeSchedule rate 0.01, exponent 1, takerOnly true, rebateRate 0.25 on 126 of 132 open markets; 6 markets have no schedule. Taker fee = size x 0.01 x p(1-p): 0.25c/share at p 0.5. CORRECTION to my earlier "0.04" (R-070) and to the scorer docstring: the code reads each market's own rate. | gamma /events?tag_slug=mention-markets, read 24 Nov 14:07Z |
| F3 | CLOB seconds_delay = 0 on mentions markets (Dell "AI 50+" and the Seahawks announcer market read 24 Nov), so SETTLED A3's 250 ms taker hold applies | clob /markets/<cid>; SETTLED A3 |
| F4 | Tick 0.001, minimum order 5 shares | clob /markets/<cid> |
| F5 | Depth is thin: listed liquidity per EVENT $11 to $7,571 (pardon $7,571, Jensen $4,437, Dell $1,141) | gamma, same read |
| F6 | Old evidence: statistical PASS at 10c edge (paired t 3.8) but one print per bet, avg $10-15, no book at decision time, so "economically tiny", about $4.9/day FLOOR | INBOX P-018 (REAUDIT) |
| F7 | Frozen fair value: per-word causal base rate q = (wins + 2*gp)/(n + 2), gp = family rate, history only from events fully closed before this event's start; count markets ("5+ times") pool across thresholds (known defect) | it/mentions_pm_daily_scorer.py q_for; INBOX P-MEN-2000 |
| F8 | Recorder P121 records own-token books for all mention tokens (162/162 at 10:23Z) | IT dialogue P121r-health-20261124.md |

## 2. Rule (frozen; same as the forward test, no refit)
- Fair YES = q at listing; fair NO = 1 - q. Decision times: listing +0..60 min every 5 min; T-24h, T-6h, T-1h, T-15m; every 5 min over [T-6h, T].
- Arm A (TAKER): buy the token whose OWN best ask <= fair - 10c and >= 5c; walk own asks up to $200 per (decision, token), $2,000/day cap; fee per F2; 250 ms hold (F3).
- Arm B (MAKER, new level): post-only bid ONE tick above the own best bid when fair - bid >= 10c and the spread > 1 tick; never join behind an existing level (MFW settled lesson); $200 per order; cancel at T-15m.

## 3. Nautilus node (the only simulator; no custom fill or P&L code)
| Setting | Value |
|---|---|
| node | own TradingNode, trader id PKWILLSAY-001, own paper account, own engine, own process |
| data | Polymarket live data client: order book deltas AND trade ticks for BOTH tokens of every market in scope |
| trade_execution | True |
| queue_position | True |
| liquidity_consumption | True |
| use_message_queue | True |
| latency | 250 ms (A3) on the live node; 0 / 1,000 ms cells offline on recorded data |
| fills | MINT fill-only mapping of other-token BUY prints, de-duplicated by (token, price, size, ts_event); reuse the NBA mint_map.py rules (gate v6 PASS) |
| orders | post-only LIMIT (arm B) and IOC LIMIT at the walked price (arm A); no execution client |
An unsupported setting on the pinned version means the node does not start.

## 4. Modelling principles table (MODELLING-PRINCIPLES.md)
| s | Requirement | How |
|---|---|---|
| 2 | Power with planted edge | plant +10c fair shift on recorded books; must be detected; null run must be silent |
| 4 | Breadth | the independent unit is the EVENT (one speech/call), not the word market |
| 5 | Shrinkage | q is already shrunk to the family rate; rank cells on shrunk edge |
| 8 | No hindsight | q from closed events only; decisions at receipt time; config SHA frozen before event 1 |
| 10 | Fills not random | fill-conditional markout vs the unfilled counterfactual; informed-trader check: are arm B fills followed by the word being said or not said? |
| 11 | Regime | per sub-type and per week; top-5 share of P&L |
| 12 | Noise | settlement P&L primary (binary resolves same day), 10-min markout secondary |
| 13 | Sequential stops | 10 blind events, always-valid 95% interval per cell; success lower > 0, futility upper < 0, 60 events max |
| 14 | Capacity | $/day only from measured own-ask depth at decision (F5); FLOOR label until then |

## 5. Start gates (none true today)
G1 owner or Reviewer builds the node config; IT pastes the Nautilus version and confirms each setting. G2 live probe: both tokens of one live mention market show book deltas AND trade ticks within 15 min of start. G3 frozen config (q snapshot file SHA, thresholds, caps) committed before the first event. G4 planted-edge run passes on P121 books. G5 one NEEDS-NICK row (server code: one more paper process on Prime). Default if unanswered: not started.

## 6. Stand-alone vs bar
Not shown to clear $200/day: F5 depth and F6 history say capacity is small. Settles it: measured own-ask depth at decisions from P121 (books exist from 24 Nov 09:25Z) and 10+ events through the stops.

Confidence 6/10 as a spec: facts F2-F5 are read live today; the Nautilus class names for the Polymarket data client are UNVERIFIED (as in NBA v6). To reach 9: IT confirms the settings on Prime's version; the gate signs the table.
