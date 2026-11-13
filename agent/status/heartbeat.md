# Fleet heartbeat — 2026-11-12 ~03:45Z (cron sweep)
- Live captures both running: thesports capture-b (pid 2818605, final-topics-32295b, ts_mqtt 6.2G live 03:47Z) and thesports-capture-cricket (pid 1829238, scope active, timeout 172800).
- DATA GAP: origin newest slim ts_mqtt = 21:10Z Nov 11 (f80025b293 @00:23Z); capture live 03:47Z. ~6.5h stranded; last timer run push_rc:1. Next timer 04:00Z (CB15 fix active).
- CB9/10/11 recorders live (netflix/charts/mentions); netflix 600s TimeoutStart flagged, self-heals per Restart=always.
- FLOOR BREACH: VOL2 /mnt/HC_Volume_107257520 94% used, 6.3G free — below clause-8 15G floor (OPEN row D, in TO-IT). Dominant: shadow/data-v2 64G + thesports raw 16G; no box route yet (writers.conf pkarbs row points at empty shadow/data).
Drives: / 50% (18G free), /mnt/...107247271 65% (16.7G free), VOL2 94% (6.3G free, FLOOR BREACH).
UTC: 2026-11-12 ~03:45Z.
