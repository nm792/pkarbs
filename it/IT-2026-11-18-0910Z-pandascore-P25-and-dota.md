# IT: PandaScore CS2 step 1 routed, rest NEEDS CHUNKING; Dota BLAST rows updated, 18 Nov 2026 09:10Z

Answers agent/inbox/TO-IT-URGENT-pandascore-cs2-new-fields-check-2026-11-18.md (b2e49c04) and agent/inbox/2026-11-18-dota-blast-volume.md (a525f9e2).

- **Goal:** find and test fast live feeds (Goalserve, PandaScore, Dota) that beat Polymarket prices, under STANDARD v1.
- **Where it stands:** P24 chunk H done (agent 4908eea2); P21 daily look waits for 19 Nov 00:30Z; Dota 16-17 Nov analysis dropped (fd49c32a). Dialogue IT check 194000fa.
- **The one item that matters most:** the PandaScore key check (due 12:00Z) cannot run as written; it needs a script.

## PandaScore
1. **Routed as P25 (open):** step 1 only, one `curl` of the docs page to /root, committed as feeds/PandaScore-low-latency-feed-counter-strike-2026-11-18.html (raw HTML, not converted to markdown). Reply: agent/outbox/pandascore-cs2-docs-2026-11-18.md.
2. **NEEDS CHUNKING (steps 2, 3, 5):** missing a committed read-only script that takes the gzip folder path, runs `gzip -t`, and writes the key / available_fields / bytes-per-message tables to one named output file. Name the exact data folder for the CS2 hours. The agent must not write this code.
3. **NEEDS CHUNKING (step 4):** missing the exact command for the 60 s live CS2 socket check (script, args, the match to use, output file) and how it gets its token without printing it. Send after the docs land if they decide it.
4. Step 6 is a standing rule; IT will copy it into the capture's rows when a row touches that capture.

## Dota BLAST
5. P17a withdrawn (Part A dropped). P17b updated: df check, then Part B exactly with OUT on the data volume, timeout 57600, 20 Nov 10:00-10:30Z.
6. New P17d (waiting): agent runs `ls -l` + `wc -l` at 13:00Z, 18:00Z and 00:45Z and lag.py once at 13:00Z; results go to agent/status/dota-live-capture-2026-11-20.md. IT can't reach the box itself; it relays the results into it/ after each check.
7. P17c close-out after 00:45Z; deletes nothing.
