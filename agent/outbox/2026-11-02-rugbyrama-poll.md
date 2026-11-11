# Outbox: Rugbyrama 15s widget poll — section read, add plan confirmed, windows hold

From: Hermes (server member). Replying to agent/inbox/2026-11-02-rugbyrama-poll.md (2 Nov).

## Read: task section "Added 2 Nov 2026 (Nick approved, 15:44Z)"
Confirmed present in agent/tasks/TASK-rugby-top14-capture-2026-11-07.md:
- Rugbyrama widget polls **every 15 s**, first-seen clock (not broadcast latency), inside capture.py as a **fourth async task** in the same process + memory cap — no separate process, no change to existing gates.
- Honest User-Agent. Non-200/parse error logged not fatal; 3 consecutive failures = that match's clock FAILED (report-only).
- Match IDs from rugbyrama.fr results pages (checked 2 Nov). Poll window = kickoff minus 30 min to full-time plus 15 min.
- Files copied to /mnt/project-files/rugby/live-2026-11/ with other outputs.
- Pass/fail separate: PASS if ≥1 event first-seen recorded during play; FAIL if widget polled whole match with no event. Lag reported as "first-seen at a 15 s poll", never broadcast latency.

## Hold before any window (per section)
- **UNRESOLVED 2-match fixture conflict** (section): Rugbyrama 61242 Toulouse v Clermont shows Sat 13:30 UTC vs gamma 15:35 UTC; Rugbyrama 61243 Vannes v Bordeaux-Begles Sun 14:00 UTC vs gamma Sat 13:30 UTC. Windows A/B follow gamma. Section: **"Do not run any window until the coordinator confirms which source is right."**
- The capture.py edit (4th Rugbyrama task) is a code change — held pending this confirmation; the edit is only exercised 7-8 Nov and the section itself gates the run on the coordinator, so there is no run to prep against until that clears. Will wire the poll in once the match list / window times are confirmed and after the code-change gate is cleared.

## Waiting on
- Coordinator: which fixture source is right (Rugbyrama vs gamma) for those 2 matches, before any window. Not a Nick item (no cost/merge/restart).
