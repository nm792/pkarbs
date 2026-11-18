# IT to PK arbs, 18 Nov 2026 21:10Z: agent budget answer, P35 gate lowered, P37 routed

1. **Goal.** Checked PandaScore and Goalserve Dota/tennis lead results, each Polymarket token priced from its own book.
2. **Where it stands.** No agent model commit since 19:31Z (trading-test dialogue cb2e93c2); P34 open since 19:40Z with no output (OPEN.md, dialogue f2167dbd). IT has written "AGENT STALLED since 19:31Z" at the top of NEEDS-NICK.md (f2167dbd).
3. **The item that matters most:** the stall, not the queue order. Nothing routed tonight runs until a model session lands again.

## Your 20:50Z budget ask (a-e)
a) The agent's model calls are billed by its model provider's portal (the source of Nick's usage export, dialogue/usage/BASELINE-2026-10-08_to_11-08.md). IT does not hold the account; it is Nick's.
b) Balance left: **not known to IT**; only Nick can see it. Per-session cost: **not measured** (status/WAKE.tsv logs model requests as `not_measured`). Last measured figures: 8 Oct-8 Nov $213.63 model cost, ~110k input tokens per request (BASELINE); 14 Nov $8.06 by 10:40Z, 3,879 requests at ~96k tokens each (OPEN.md COST RULE). Anything beyond that is unsupported.
c) Reset or run-out date: **not known to IT**; Nick knows.
d) Top-up step: Nick does it, on that provider's billing page. IT has put the exact ask (balance, reset date, top up yes/no and amount) in NEEDS-NICK.md. IT cannot confirm the stall is the budget; it could also be a gateway fault.
e) Order on what is left: unchanged, P34, P35, P30, then P37, P31, P32, P36. Copying P34 inputs to the storage box is not routed: the box login failed on 16-17 Nov (your note), and copying would itself need an agent session. If you want it, send the exact source paths, destination folder and command as a chunk.

## Routed (OPEN.md, f2167dbd)
- **P35 amended:** start gate lowered from 20 GB to **17 GB** free (15 GB floor + your 45 MB/h x 37 h = 1.7 GB worst case). Not 2 GB: the 15 GB floor stays for other jobs. The volume had 20.7 GB free at 21:00Z (DISK.tsv), so it would start under either gate. Your hourly gzip crontab line is added as step 4, verbatim, with `crontab -l | grep pmdota` as proof.
- **P37 new:** your six read-only PandaScore listing commands, verbatim, output to agent/status/pandascore-files-2026-11-18.md; first row of the next session, before P31.
- **Not routed:** the 21 Nov crontab removal ("add a second line") has no exact command. Send the exact line, or IT routes a removal row after 20 Nov 09:30Z when you ask.
