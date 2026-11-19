# URGENT to IT: the server agent is not picking up work. Restart or re-dispatch it, then run PS and PL-S0 first (output due 15 Nov 09:00Z)

From: the results thread, 15 Nov 2026, 08:05Z, on the coordinator's instruction (Nick's rule of 13 Nov: stalls go to IT as a new urgent issue plus inbox note). New note, not a repeat on #348/#347.

Facts, all from the repo history on claude/project-thread-vg2ckg:
- Last real agent commit 05:30Z (temperature task). Since then only no-model heartbeats (06:00Z, 07:00Z, 08:00Z).
- IT routed PS (#348) first at 06:10Z, due 07:30Z. No outbox or status file for it exists at 08:00Z. PL S0 (#347, due 09:00Z) is also absent.
- Nick has been told there are no lead results from data captured since 13 Nov. This is the blocker.

Ask, in order:
1. Check whether the agent session is alive and working; if it is not, restart or re-dispatch it. Say in `agent/inbox/IT-REPLY-*` what you found.
2. PS first: run `feeds/ps_lead_test.py` exactly as written in `agent/inbox/TO-IT-URGENT-pandascore-lead-test-run-script-2026-11-15-0540Z.md` (setup check first, computed table only, no raw to git). Output `agent/outbox/ps-lead-test-2026-11-15.md` plus the JSON under agent/status/.
3. Then PL S0 as in `agent/inbox/TO-IT-URGENT-LoL-final-locked-test-setup-check-first-2026-11-15-0520Z.md`.
4. Deadline 09:00Z for the PS table and the S0 report. If a step cannot finish by then, commit what exists, labelled partial, with n shown.

Pre-registrations are unchanged; do not edit them.
