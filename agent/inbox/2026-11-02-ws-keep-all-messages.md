# Inbox: keep all sports-WS messages during the CS2 logger run

From: project thread (PK arbs), 2 Nov 2026 07:00Z
To: server agent (Hermes)

Please change nothing in the running CS2 logger except this: keep every message from the Polymarket sports WebSocket (wss://sports-api.polymarket.com/ws) in the raw capture, not only the CS2 frames.

- Keep all league messages, including cricket, WTA, and college basketball.
- Pay particular attention to cricket messages around the Nepal Premier League match on 3 Nov 2026. Save those in the raw capture even if the logger's filter would drop them.
- Write them to the same raw capture file as the CS2 frames, and mention any cricket frames in your status file.
- Do not restart the logger, and do not change its memory or runtime limits, to do this. If the change needs a restart, tell us in agent/outbox/ first.

Reply in agent/outbox/2026-11-02-ws-keep-all-messages.md. Confirm what you changed, or say what blocks you. Nick is not needed for this.
