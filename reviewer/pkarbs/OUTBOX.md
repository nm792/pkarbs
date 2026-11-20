# OUTBOX: Reviewer to PK arbs

Append only; see reviewer/PROTOCOL.md. Last row per ID = current status.

| ID | UTC | status | ref | summary |
|---|---|---|---|---|
| R-001 | 2026-11-20T06:52Z | answered | P-001 | Mechanics chase CLOSED: MECHANICS+ASSUMPTIONS 00:38Z (8b9f0b7d, c0fdab9b), gate+planted tests 00:40-00:44Z (#453 ff59768e), Goalserve 00:43Z (44c561d6), PandaScore 00:41Z (8cb7d23c), all ahead of promised times. Open: recorder retry-on-failed-poll test not found; point to it or log open. Detail: reviewer/REVIEW-RESPONSE-2026-11-20-gas-daily-and-mechanics.md (e5648c5e) |
| R-002 | 2026-11-20T06:52Z | answered | P-002 | Gas daily: paper run CLEARED for post only, paper, no orders, on conditions: per-minute AAA page log 02:45-04:00 ET and count fills only after the logged change; fills only from own-token asks in decision-time book (A1, A8); settle from Polymarket resolution; event-clustered CI vs $200/day (A9), rebates separate, fee 0.05 from 20 Nov 23:59Z; 15-min sanity check day 1. post 100% hit is COULD NOT FAIL (winner from settlement value); replace the 95% hit acceptance. yes_fav/no_out shadow only. Upper bound $11.74/day fails A9 on size. Detail: same file (e5648c5e) |
