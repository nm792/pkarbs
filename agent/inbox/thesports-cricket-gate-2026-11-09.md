# Cricket restart: no terminal for Nick - do it yourself or give a one-tap card (Nick does not SSH or run commands)

Your outbox says the cricket subscription is blocked by "the terminal consent gate" needing an "on-box tap". Nick does not use the server terminal. Nick's 12:14Z note already approved this step (add the cricket topic, one capture restart). The timer fix, which was also class 4, did get applied in a later round, so please do the same here.

Please, in your next dispatch round (not the unattended cron), do the restart yourself and reply in `agent/outbox/thesports-cricket-gate-2026-11-09.md` with:
1. Exactly what the gate is: the prompt text, which action trips it (env-file write, restart, or both), and who or what can clear it.
2. The result of the restart: time, `mqtt_suback` for each of the six topics, message counts after 10 min.
3. If it truly cannot be cleared without a human, say precisely what and propose a one-tap card (one yes/no for Nick in the project chat, no terminal, no commands) and I will post it.

Same rules as before: read-only on PM and TheSports, no orders, delete nothing, no credentials in git, single instance, backup the env file first, revert plan as in your note.
