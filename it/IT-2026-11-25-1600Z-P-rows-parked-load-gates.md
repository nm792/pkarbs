# IT 2026-11-25 16:17Z (corrects 16:00Z): P rows stay open under the new light scorer gate

1. Goal: score PK recorded data (MECE-NO, trial-feed timing, PCE release, NVDA gap fade) and keep the PK recorders shipped and readable.
2. Where it stands: every P run from at least 10:53Z to 15:54Z found no runnable row (load 10.42, MemAvailable 2,133,644 kB at 15:54Z; trading-test dialogue RUNLOG-P 748657f0). The reviewer's 1605Z reply set a light scorer gate (load1 under 12, MemAvailable 2,000 MB or more, MemoryMax 1G, CPUWeight 20, nice 19, ionice -c3, timeout 900), and IT put it in PROMPT-P at 16:15Z (dialogue 95af1b2e).
3. Most important: P159 runs first under that gate, then P150, P147, P146, P148, P149, P157, one per run.

Items:
- The 16:00Z draft said IT would park P146-P150, P152, P157 and P159. Your gate came first, so IT did not park them; they stay open in OPEN.md (dialogue 92a6fdfe).
- P143 is open only for the IT 16:15Z gap-time step: write the next E=0 time as NOT BEFORE in its status.
- P139b, P139c, P138, P106b, P106c moved to OPEN-WAITING.md with their gates unchanged.
