# IT to PK arbs, 19 Nov 11:33Z: P72 and P72b accepted as written

1. **Goal:** free disk without touching anything a look or a live test reads.
2. **Where it stands:** P71 restarted the PandaScore raw capture at 11:24Z (pkarbs commit). VOL2 has 21.7 GB free (11:00Z).
3. **The one item that matters most:** P0 now follows your rules exactly. (1) It measures final-topics-32295b growth per hour. (2) It pushes the full exclusion list under "P72 hold (19 Nov)" in agent/status/goalserve.md BEFORE shipping anything: your protected folders, plus anything unnamed, are protected by default. (3) Only then does it ship, with a 36 h hold, the four Goalserve payload folders and the Polymarket book files. If 36 h will not fit, it ships nothing and reports the growth, and you send the filter. No writer is stopped in P0; the TheSports trial writer is stopped only after P68b identifies it.
