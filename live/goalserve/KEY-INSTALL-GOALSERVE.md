# Installing the Goalserve trial credentials on the server (Hermes does it; Nick never runs commands)

1. Goalserve emailed Nick a trial API key and the login name emblematic07. Nick sends them to Hermes in his own direct chat with Hermes (as for TheSports). Never in a Claude thread, Git, a PR, an issue, or any agent/inbox|outbox|status file.
2. Hermes writes `/etc/pkarbs/goalserve.env` from its own process (not on a command line, so nothing lands in shell history):
   ```
   GOALSERVE_KEY=<api key>
   GOALSERVE_USER=emblematic07
   ```
   Then `chmod 600`, owner root; `/etc/pkarbs` stays mode 700.
3. Confirm the server's public egress IP equals the IP Goalserve whitelisted (157.180.24.89). If it differs, tell IT in agent/inbox at once; the WebSocket and REST in-play feeds will refuse other IPs. Do not tell Nick to ask Goalserve unless IT confirms it differs.
4. Never print, copy, commit or message the key. The capture code must replace the key with `[R]` in every URL and log line it writes (the key sits in the URL path of getfeed requests). Status files say only "credentials installed: yes/no".
5. The test starts by itself when the env file exists: agent/tasks/TASK-goalserve-v2-2026-11-12.md.
6. When the trial ends or Nick says stop: delete `/etc/pkarbs/goalserve.env`.
