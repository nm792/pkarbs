# TO IT, URGENT: add check D (timestamps and message lag) to the PandaScore audit, due 04:00Z

Nick asked (02:40Z): "Panda's lead is worse than TheSports?" A feed called low-latency that sits about 30 s behind the price needs its setup checked first.
The audit rule (TO-IT-URGENT-pandascore-lead-AUDIT-locked-rule-2026-11-16-0215Z.md) is unchanged. Run `feeds/ps_lead_audit.py` from the default branch: it now also does check D. Deadline is still 04:00Z.

Check D reports, with the field names quoted:
1. Which feed clock the test used: `recv_ns` (our receipt time on the capture host). `updated_at` (PandaScore's send time) is NOT used for the lead.
2. Which price clock: `ms` on the Polymarket book row (same host). `sent` is the exchange send time, logged only. Median `ms - sent` was 156 ms.
3. Lag: `recv_ns` minus `updated_at` in seconds, by message kind (messages that carry a counter increase vs others).
4. CS2 round-win delay: time from the first message where every player of one team has `player_alive` false (from `current_round.<team>.players[].alive`) to the message where `round_score` increases. If round-win messages arrive late while kills and alive flips arrive early, the price is reacting to earlier messages.

Please also quote any evidence that the server clock is in sync (chrony or timedatectl output) in your report.
Report in `agent/outbox/ps-lead-audit-2026-11-16.md` plus the JSON. State plainly what each number means. Do not call any result a fail before D is read.
