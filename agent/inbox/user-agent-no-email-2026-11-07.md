# User-agent change before the 12:30Z preflight (project thread, 7 Nov 09:20Z)

Nick's email address is not to be sent to third parties. Supersedes check 1 in rugby-preflight-checks-2026-11-07.md.

- Use the generic UA `pkarbs-research/1.0` everywhere: ESPN, Rugbyrama, Polymarket REST and websockets, TheSports and any other capture. No email or contact string in any header.
- The rugby harness (agent/tasks/rugby-top14-capture.py), the rugby task file and hltv-scorebot/capture.js are already changed in the repo. Pull before the 12:30Z preflight. If another script on the server still carries an address, change it before its next start; do not restart a running capture just for this.
- The ESPN scoreboard returned 403 from the project sandbox with the old UA and 200 with the generic one. Confirm the status at preflight and write it in the status file.
