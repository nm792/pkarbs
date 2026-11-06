# thesports-trial status
- **state**: BLOCKED — credentials not installed
- **last heartbeat**: 2026-11-06T10:18Z UTC
- **credentials installed**: no (`/etc/pkarbs/thesports.env` absent; `THESPORTS_USER` not found on box)
- **errors**: none; no MQTT connect possible without creds
- **output paths**: none produced (`ts_mqtt.jsonl.gz`, `log.jsonl.gz` not yet started)
- **waiting for Nick**: YES — Nick to forward the TheSports trial user/secret/topics in DIRECT chat (never in a repo/thread), then Hermes writes `/etc/pkarbs/thesports.env` (chmod 600) and starts Part B (LoL first, Worlds semis 7-8 Nov).
