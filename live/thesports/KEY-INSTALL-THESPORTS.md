# Installing the TheSports trial credentials on the server (Hermes does it; Nick never runs commands)

1. TheSports emails Nick a trial **user** and **secret** (and, for MQTT, a list of topics). Nick forwards them to Hermes in
   his own direct chat with Hermes. Never in a Claude thread, Git, a PR, or an agent/inbox|outbox|status file.
2. Hermes writes `/etc/pkarbs/thesports.env` from its own process (not on a command line, so nothing lands in shell history):
   ```
   THESPORTS_USER=<user>
   THESPORTS_SECRET=<secret>
   THESPORTS_TOPICS=<comma list of topics from TheSports, or leave the line out to subscribe to '#'>
   ```
   Optional lines, only if TheSports gives different values: `THESPORTS_MQTT_HOST` (default mq.thesports.com),
   `THESPORTS_MQTT_PORT` (443), `THESPORTS_MQTT_PATH` (/mqtt), `THESPORTS_MQTT_TRANSPORT` (websockets or tcp),
   `THESPORTS_POLL_PATHS` (comma list of HTTP paths to poll every 2 s for comparison, e.g. the tennis/esports live endpoints).
   Then `chmod 600`, owner root; `/etc/pkarbs` stays mode 700.
3. Never print, copy, commit or message the user/secret. capture.py replaces both with `[R]` in every line it writes; the
   copy-out step re-checks with `zgrep -F -l -f <(grep -E '^THESPORTS_(USER|SECRET)=' /etc/pkarbs/thesports.env | cut -d= -f2- | grep -E '^.{6,}$')` (must print nothing).
   Status files say only "credentials installed: yes/no".
4. When the trial ends or Nick says stop: delete `/etc/pkarbs/thesports.env`.
