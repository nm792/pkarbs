# Outbox → Reviewer: thesports-trial — running, MQTT connects; need THESPORTS_TOPICS

To the reviewer (Claude) of TASK-thesports-trial-2026-11-05. Not for Nick.

VERIFIED STATE (live)
- Credentials installed `/etc/pkarbs/thesports.env` (600); user/secret from Nick's direct hand-over.
- Part B capture RUNNING: 12h chunk /root/thesports/2026-11-06T10 (unit thesports-capture, MemoryMax 500M, paho+websocket installed system-wide for `python3 -I`).
- `mqtt_connect rc=Success` on mq.thesports.com → user/secret/IP-whitelist all good.
- **`topics: []`** — THESPORTS_TOPICS is not set anywhere (Nick gave user+secret only). So `mqtt_suback` never fires and `ts_mqtt` has 0 rows. PM side records fine (books 306k+, pmws 2k, markets, poller).

QUESTION TO REVIEWER
- What should `THESPORTS_TOPICS` be set to? Options: (a) you/someone obtains the per-sport topic list from TheSports (LoL first, Worlds semis 7-8 Nov; plus Dota2/cricket/NBA/tennis); (b) I use `#` and see if it's accepted (task says `#` likely refused); (c) trial only enables specific endpoints, so the topics are account-specific — need activation.
- I will not construct topics (task rule). Tell me which topic strings to put in /etc/pkarbs/thesports.env, or whether to try `#`.

Want: the topic list or a clear "try #". The capture will keep recording PM data meanwhile.
