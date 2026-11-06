# status: thesports-trial (TASK-thesports-trial-2026-11-05)
- Capture 2026-11-06T10 chunk RUNNING healthy: books 610 M (583,892 rows @13:31Z, growing), pmws 4525, markets 124, discover_pm 248 tokens, mqtt_connect rc=Success @start.
- Credentials installed: yes (THESPORTS_USER/SECRET in /etc/pkarbs/thesports.env). Values never printed.
- **THESPORTS_TOPICS=# trial: APPROVED (task file, PR #164, 12:32Z) but NOT yet applied** — the /etc/pkarbs/thesports.env edit is a system-config write that is consent-blocked in the unattended cron terminal (no user to clear the dangerous-command gate). Capture left running (healthy); the approved edit+restart + mqtt_suback rc record remain pending until the env write is cleared on the box / next interactive turn.
- suback: not yet recorded (no topics subscribed; THESPORTS_TOPICS line not present, only USER/SECRET).
- No ts_mqtt file yet (nothing subscribed). books/log/markets/pmws all committing via share.
- next: apply THESPORTS_TOPICS=#, restart chunk (12h), record mqtt_suback rc per inbox 12:08Z + task Part B.
