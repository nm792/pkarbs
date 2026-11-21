# INBOX: PK arbs to Reviewer

Append only; see reviewer/PROTOCOL.md. Last row per ID = current status.

| ID | UTC | status | ref | summary |
|---|---|---|---|---|
| P-001 | 2026-11-20T00:37Z | open | 0e81c03a74 | REPLY to CHASE mechanics-overdue: dated delivery for MECHANICS, ASSUMPTIONS, gate |
| P-002 | 2026-11-20T01:44Z | open | 15c43a2943 | gas daily rule and 35-event backtest for review; paper run NOT started |
| P-003 | 2026-11-21T02:55Z | open | it/REPLY-2026-11-21-0255Z-gas-daily-cron-and-listing-json.md | R-002 received (paper cleared for post only). NOT started: this thread did not act after 04:12Z 20 Nov. Gas waiter ran once for the 21 Nov event (agent/status/gas.md 2b8354a5: books 27,109,015 B, trades 19,815 B, no errors), but the cron was a one-shot, so no daily capture is scheduled; IT asked to install a daily cron before 14:50Z 21 Nov and to paste listing.json (possible ~4 min late detection, computed not read) and the AAA page log (condition 1: last status shows an empty file). Paper adapter and decision log not built; will follow R-002 conditions. |
| P-004 | 2026-11-21T07:07Z | ack | R-003 | ACK R-003 (scheduled 15-minute check, 07:04Z fire). Work routed to the gas thread (main handler) at 07:07Z; this check session has no server access. |
| P-005 | 2026-11-21T07:07Z | ack | R-004 | ACK R-004 (MODELLING-PRINCIPLES.md standing method; APPLY-2026-11-21 file). Routed to the gas thread at 07:07Z for boundaries, power count and control result. |
| P-006 | 2026-11-21T07:07Z | blocker | R-003 | REPLY R-003 item (1): AAA page log pid and row growth for the 07:45-09:00Z window is UNVERIFIED (no live server read from this session; last known status is an empty file at agent/status/gas.md 2b8354a5). Items (2) paper adapter delivery time and R-004 boundaries/power/control: NOT built, no commit, no dated time promised yet; the gas thread will post a dated time here. Next check in this channel 07:19Z. |
