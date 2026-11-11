# TASK (read-only diagnosis, reply in agent/outbox): why did discover_pm skip these listed tennis matches?

Polymarket lists these (gamma, tag tennis, moneyline) but we have NO books or market rows for them:
wta-liu-eala-2026-11-08 (gameStart 08:00Z 8 Nov), atp-staehel-tange-2026-11-07, atp-langmo-vujic-2026-11-07,
atp-imai-kouzmin-2026-11-07, atp-saitoh-takahas-2026-11-07, atp-watanuk-kumstat-2026-11-08, atp-wong-watanuk-2026-11-07.

Please grep the capture log for each slug and report: seen by discover_pm? Rejected by which filter (offset cap, 'more-markets' skip,
gameStartTime window, MKT_TYPES, end_date_min)? Also report whether markets.jsonl in the 12:03Z export is complete (row count, last ms).
No code change in this task. If a filter is the cause, propose the patch in outbox and Nick will approve it on a card.
