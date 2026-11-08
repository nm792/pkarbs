# TheSports trial — Part B cannot start (credentials not installed)

**APPROVALS NEEDED:** none.

**RESULT**
- `/etc/pkarbs/thesports.env` is ABSENT on the box; `THESPORTS_USER`/`THESPORTS_SECRET` are not present anywhere on disk (searched /etc, /root, /root/.hermes, /root/secrets via variable name).
- Per TASK-thesports-trial-2026-11-05 (Credentials step) and the 2026-11-06 GO note's step 1, this is the ONLY blocker: "if the file is missing, write status 'credentials installed: no' and reply in outbox".
- Part B not started — cannot run capture.py against mq.thesports.com without user/secret; no topical subscribe is possible.

**DATA**
- `agent/status/thesports-trial.md` (this reply) states `credentials installed: no`.
- No credentials were written, printed, copied or committed (honest state: absent).

**OPEN / NOT VERIFIED**
- Blocker: Nick to send trial user/secret/topics via DIRECT chat (per KEY-INSTALL-THESPORTS.md rule: never in a Claude thread/Git/status file). On receipt, Hermes writes the env file and starts Part B immediately, checking LoL first (Worlds semis 7-8 Nov, final 14 Nov).

**Count**: notes run 1, outstanding 1 (TheSports Part B, credential-gated), PENDING open 0.
**Context**: YES — waiting on Nick for the credential deliverable; nothing further runs until it lands.
