# To Hermes / IT: Goalserve trial, install the key and start (12 Nov 2026)

Nick registered for the Goalserve Full Package trial. Goalserve whitelisted the server's IP (the address is in Nick's Goalserve email and is not written in the repo) and sent test feeds. Nick does not use SSH.

Do now, in this order:
1. Read live/goalserve/KEY-INSTALL-GOALSERVE.md. Nick will send the key and login to you in his direct chat with you. When it arrives, write /etc/pkarbs/goalserve.env as described. Never commit, print or copy the key.
2. Check that this server's public egress IP is the whitelisted one. If not, raise it to IT in agent/inbox immediately (say "IP mismatch" only).
3. Run agent/tasks/TASK-goalserve-v2-2026-11-12.md. IGNORE the two older Goalserve task files: they are marked SUPERSEDED.
4. Write a status in outbox/status within 30 min of the env file existing, and every 30 min while blocked. Escalate to IT at once if blocked; do not wait overnight.
5. Hard checks before the first full run: (a) does https://inplay.goalserve.com/inplay-tennis.gz load from this server with and without the key; (b) can the WebSocket token request work (POST https://live.goalserve.com/api/v1/auth/gettoken). Report both yes/no in status.
