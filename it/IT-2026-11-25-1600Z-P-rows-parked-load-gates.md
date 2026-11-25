# IT 2026-11-25 16:00Z: all open P rows parked on load gates; please restate the gates

1. Goal: score PK recorded data (MECE-NO, trial-feed timing, PCE release, NVDA gap fade) and keep the PK recorders shipped and readable.
2. Where it stands: every P run since at least 10:53Z found no runnable row. At 15:54Z load was 10.42, MemAvailable 2,133,644 kB, VOL2 12.62 GB (trading-test dialogue RUNLOG-P, 748657f0). The box runs 10 MFW cells and 4 Temperature cells at top priority, so load is unlikely to fall under 3.2 soon.
3. Most important: the gates, because none of P146-P150, P152, P157, P159 can run under them, and each empty P run is a paid agent wake.

Items:
- Parked to OPEN-WAITING.md (IT 16:00Z): P150, P147, P148, P149, P152 (load under 3.2); P146 (load under 3.2 and 3 GB free memory); P159 (load under 8); P157 (after P150, which it needs).
- To reopen any of them, send a restated gate that can be met at load around 10 (P151c ran at load 6.43 with a load-under-8 gate in a MemoryMax 1G, CPUWeight 20, nice 19, ionice -c3 scope, timeout 900). Name the row order you want. P159 (PCE score) looks cheapest; a restated gate for it alone would give PK a row now.
- Nick's rule of one PK row per 2 h cannot be met under the current gates; IT has put this in NEEDS-NICK.md.
