# TheSports activated cricket + LoL; trial valid to 16 Nov (Nick, 12:14Z 9 Nov) - routine step, no further approval needed

TheSports replied: Cricket and LoL are now activated. Topics: `thesports/cricket/match/v1`, `thesports/lol/match/v1` (plus basketball, tennis, dota2, csgo as now). Trial ends 16 Nov. We already use MQTT for the five existing topics, so no protocol change.

Please (read-only, no orders, delete nothing, no credentials in git, single instance, charter disk check):
1. Add `thesports/cricket/match/v1` to THESPORTS_TOPICS (keep the other five) and restart the capture once, so all six are subscribed. Reply in `agent/outbox/thesports-cricket-lol-mqtt-2026-11-09.md` with: restart time, `mqtt_suback` result for each of the six topics, and message counts per topic after 10 min and after 1 h.
2. If cricket or LoL returns a suback error or zero messages, paste the exact error text (Nick will forward it to TheSports, who asked for it).
3. Add cricket and LoL to the PM book/market recording (Worlds ends 14 Nov; any live cricket match) and to the diary refresh, and include them in the 2 h export.
