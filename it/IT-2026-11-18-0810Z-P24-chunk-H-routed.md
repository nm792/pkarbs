# IT note: P18 closed, chunk H routed as P24 (PK arbs, 18 Nov 2026, 08:10Z)

1. **Goal:** the first Goalserve esports look on 19 Nov ~01:00Z, with tennis in parallel.
2. **Position:** E1b smoke ALL PASS at 07:48:54Z, smoke exit 0, files=24 (agent/status/goalserve.md, pkarbs bab1584c); OPEN P18 archived in IT check 0ace2f94 (trading-test dialogue).
3. **Most important:** chunk H (9aa268af) is routed as OPEN P24, `open`, read-only, due 10:00Z, because the first look needs the 18 Nov poll log and hour files.

Items:
- P24 runs chunk H's bash block once and must not restart the capture; if it is down, the agent says since when, and a restart needs a separate chunked note.
- P21 (chunk F): its dependency (P18 ALL PASS) has landed. It stays `waiting: until 19 Nov 00:30Z`, because a waiting row wakes no paid session and the agent cannot act before the slot. IT sets it `open` at the first check after 00:30Z.
