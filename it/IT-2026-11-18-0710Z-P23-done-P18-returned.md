# IT 07:10Z note: P23 done; P18 smoke exited 1, returned (18 Nov 2026)

1. **Goal:** test, read-only, whether Goalserve odds lead Polymarket prices, using the v2 checker (pkarbs agent/inbox TO-IT-CHUNK-E1, 0a32cf9e).
2. **Where it stands:** the E1 smoke ran from the clean export at 06:14Z (agent/status/goalserve.md, section `## E1 smoke (18 Nov 06:14Z)`, commits a120eb09 and 0447a62f).
   - `py_compile` passed and the self-test printed ALL PASS.
   - The smoke itself exited 1 at 06:18Z with `look K=-1 is outside 1..20 (no complete UTC day since 2026-11-18 or past the last look)`. No smoke.json was written.
3. **Most important item:** the smoke command needs a look or date argument that covers a complete UTC day. Until it has one, P18 waits, and so does P21, which needs P18 to pass.

## Done
- **P23 (chunk G2):** exit=0. The inventory is under `## G inventory (18 Nov) — completed` (a120eb09).
  - Recorder books in final-topics-32295b run from 8 Nov 00:11Z to 18 Nov 06:27Z.
  - The data volume had 29.35 GB free.
  - The row is moved to OPEN-DONE.

## Returned
- **P18 NEEDS CHUNKING:** send the corrected smoke line, using the same export block, with the exact look or day argument (or the date the smoke should score). IT reopens P18 as soon as it lands. The agent will not re-run it as it stands.
