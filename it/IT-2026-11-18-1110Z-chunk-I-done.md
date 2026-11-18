# IT to PK arbs: chunk I (P26) done (18 Nov 2026, 11:10Z)

1. Goal: find and test cross-venue arbitrage edges (Goalserve/PandaScore feeds vs Polymarket) on PK arbs markets.
2. Where it stands: Goalserve tennis probe ran once from a clean export of 322d8129 (pkarbs agent/status/goalserve.md, commit f83f0eba, 10:42:30Z): exit 0, files 2, polls 44709, events 0, `market_names_used {}`, `league_prefixes_seen {"unparsed": 95671}`.
3. Most important item: events 0 means the probe's parser matched nothing in the tennis payloads. The probe ran, but it found no tennis data it could use. Any tennis verdict needs a parser change from PK arbs first. IT does not route code changes to the agent.

Items
- P26 archived as done (dialogue OPEN-DONE, IT check e4bfacbf). The agent says the local 06/07 hour files were missing and it took the same two files from the `<box>` copy. Please confirm that is acceptable.
- No PK arbs row is `open` now. P21 waits for 19 Nov 00:30Z; P17b/d/c wait for 20 Nov. P16/P16s still wait on your ruling about the 1.98 GB of untracked files (since 17 Nov 16:56Z).
- If you want a follow-up probe with a fixed parser, send a chunked note: one ask, an exact script at a commit, the output file and a one-line done check.
