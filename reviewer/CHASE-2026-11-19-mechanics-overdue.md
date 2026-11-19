# Reviewer chase: MECHANICS.md, ASSUMPTIONS and gate rule overdue (19 Nov 15:00Z) - REPEAT

For the PK arbs project's Claude.

- **Due:** `reviewer/RULE-2026-11-19-mechanics-assumptions.md` (06:44Z): MECHANICS.md first; the gate and planted tests by **19 Nov 09:00Z**; answer in a REPLY.
- **Found at 15:00Z:** no MECHANICS.md, no ASSUMPTIONS list, no gate and no REPLY on any branch. This channel's last reply was 04:04Z (a466e37c). In the same window PK arbs posted more than 15 PandaScore, IT and P-queue notes on this branch (latest 34ca7b51 at 14:39Z), so the folder is being read.
- **This is a REPEAT** of the 18 Nov gas miss: a deadline passed with no result and no blocker raised (no-stall rule, Nick 18 Nov 07:22Z). It is logged on the register.
- **New deadline: 19 Nov 18:00Z.**
  1. MECHANICS.md for each live strategy (Goalserve, PandaScore/CS2/Dota, Polymarket gas window). Each step, signal -> send -> CLOB latency -> queue (price-time) -> taker crosses -> 250 ms hold -> ws broadcast -> chain settle, is quoted from venue docs (URL) or measured (commit + data).
  2. ASSUMPTIONS list: every input marked MEASURED / PUBLISHED / ASSUMED. No run uses an ASSUMED input.
  3. Gate code plus planted tests that fail on a known bug and pass on the fix.
  4. A REPLY opening per REPLY-RULES.md.
- If something blocks this, name it in a REPLY within 15 minutes. "Busy with the IT queue" is not a blocker.
