# TO IT: Goalserve trial is waiting on the server (12 Nov 2026, 13:30Z)

Nick gave Hermes the Goalserve key and login (emblematic07) in his direct chat at about 13:11Z. As of 13:27Z there is no Goalserve status, outbox file or env-file confirmation in the repo; Hermes's last commit is 12:34Z. The trial is 30 days and every day it sits idle is wasted, and LoL Worlds final is 14 Nov.

Please, now:
1. Confirm Hermes is running and has read agent/inbox/2026-11-12-goalserve-install-and-go.md.
2. If Hermes is down or stalled, install /etc/pkarbs/goalserve.env yourself (see live/goalserve/KEY-INSTALL-GOALSERVE.md; ask Nick for the key through Hermes's channel, never in Git) and start agent/tasks/TASK-goalserve-v2-2026-11-12.md.
3. Confirm this server's public egress IP is 157.180.24.89 (Goalserve whitelisted it). Report yes/no.
4. Post agent/status/goalserve.md: key installed yes/no, IP match yes/no, inplay-tennis.gz loads yes/no, WebSocket token works yes/no.

Never write the key into any file in this repo.
