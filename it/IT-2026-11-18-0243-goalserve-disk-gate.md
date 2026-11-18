# IT: Goalserve P18, disk gate, chunks F and G (18 Nov 2026 02:43Z)

1. **Goal:** daily looks at whether Goalserve esports odds move before the Polymarket price, in the free trial (19 Nov to 8 Dec).
2. **Where it measurably stands:** test code signed at 9d4857d4 (your SIGNED note d8b1c00). E1 smoke (P18) was attempted and NOT RUN: the agent's gate check at 02:12Z found 10,917,199,872 bytes free on the data volume, under the 20 GB gate (agent/status/goalserve.md "## E1 smoke (18 Nov)", commit eaeee170). So there are no P18 exit codes to post; the blocker is disk, not the agent.
3. **The one item that matters most:** free the data volume to more than 20 GB before about 00:30Z on 19 Nov. IT routed your read-only inventory as OPEN **P22** (top PK arbs row, trading-test dialogue 0002793a): df for root and each data volume, `du -sh --max-depth=2` top 40 on the volume P18 measured, ship_raw process/crontab lines and the oldest/newest hour files in its source folder, all into agent/status/goalserve.md under `## Disk inventory (18 Nov)`. When it lands, post your deletion list (one row per path); IT routes it as written. Nothing is deleted before that.

## Your other asks
- **P18 exit codes by 04:00Z:** not possible until the gate clears; P18 is `waiting` and IT reopens it after the deletions.
- **Chunk F daily slot (P21):** the SIGNED condition is met. P21 now waits on P18 ALL PASS only; first slot 19 Nov about 01:00Z, from default-branch head at or after 9d4857d4, no --plant-c or --seed.
- **Chunk G:** routed as OPEN **P23**, right after P22, run once as written (3ecbe84c). If `git pull` fails on the dirty checkout (P16s), the agent pastes the error and waits; it does not stash. Note G also reads the data volume, but it writes nothing.
