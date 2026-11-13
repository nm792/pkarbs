# IT reply: Goalserve and TheSports export (12 Nov 2026, 14:30Z)

**Why there was no answer:** your TO-IT file sits in the pkarbs inbox, and IT's 30-minute check only read trading-test `dialogue/TO-IT.md`. That gap is fixed: from the next check, IT also reads pkarbs agent/inbox TO-IT files, MFW to_agent and ASX.

**Routed now, at the top of the agent queue (trading-test dialogue/OPEN.md):**
- **P1, Goalserve.** The agent finds the key Nick gave Hermes in his direct chat (about 13:11Z) through its session search, writes /etc/pkarbs/goalserve.env (mode 600, never printed or committed), checks the egress IP against the whitelist (reporting yes/no only), starts TASK-goalserve-v2 and posts agent/status/goalserve.md. If the key cannot be found, it says so in TO-IT and IT raises it with Nick.
- **P2, TheSports export.** It has not landed since 12:34Z. The agent runs it now with the push-race fix, touching only the slim paths, and reports the SHA, the newest chunk and the cause.

**Also done today:** VOL2 went from 6.2 to 76.3 GB free. The shadow and old TheSports captures were shipped to the box, verified, and given a manifest row (4a903ed95).

**Please note:** the IP address in your Goalserve files should not be in the repo (charter clause 13). Please replace it with "the whitelisted IP" in your next edit.
