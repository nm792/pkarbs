# Standing rule: mechanics first, no ASSUMED input, measured clocks (Reviewer 19 Nov 06:44Z)

Nick 06:36-06:39Z: "We assumed the offsets instead of measuring them ... EVERY SINGLE ASSUMPTION WE MAKE IS MORONIC" / "market microstructure comes first" / "microstructure means what MUST HAPPEN or HOW IT MUST HAPPEN" / "RTFM". Logged as a REPEAT (MFW instances: mfw-clone reviewer 2204d08c, fccaef14, 83e3ecee, 3eeb7517).

For this project, from now on:
1. MECHANICS.md. The chain of events every fill and every settlement must physically go through, each step quoted from the venue's own docs or rules text (with URL) or measured (commit + data):
   - resolution source and rule, verbatim from the live market's rules;
   - signal, send, order travel, queue priority, match only after resting, taker hold, broadcast, on-chain settlement.
   List every contradiction between your code or findings and the docs.
2. ASSUMPTIONS.md + assumptions.csv. Every input the sim, scorer or paper logger uses, with status MEASURED, DOCUMENTED or ASSUMED.
3. A gate called first by every scorer, refusing to run on any ASSUMED or missing input or on an unmeasured feed clock. Planted tests: a fill before placement, a fill ahead of queue, a take with no hold, a feed with an unmeasured lag, and settlement from the wrong source. Each must be refused.
4. Nothing ASSUMED feeds a reported result. On-chain block time is a settlement time (MFW measured it about 0-2.8 s after the match). Never use it as match time unmeasured.
Due: MECHANICS.md first; gate plus planted tests by 19 Nov 09:00Z. Answer in a REPLY.
