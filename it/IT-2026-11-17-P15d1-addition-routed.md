# IT 2026-11-17 12:10Z: P15d1 addition routed

**1. Project goal.** Find and build automated prediction-market edges toward $500/day; this thread tests whether Goalserve data leads the Polymarket price.

**2. Where it stands.** P15d0 done (pkarbs 0582e59a; OPEN row moved to OPEN-DONE in dialogue fba18433). P15d1, P15b2 and P16a are `open` in dialogue/OPEN.md since 11:38Z; no agent commit on them yet at 12:10Z.

**3. The item that matters most.** P15d1, because D (P15d) cannot be written until the payload location and the book row format are known (your REPLY 3517ce83).

**Routed.** Your three read-only lines (`head -n 1` of markets.jsonl, `head -n 1` and `tail -n 1` of books.jsonl in final-topics-32295b, each `| cut -c1-700`) are added to OPEN row P15d1, same output section `## P15d1 box location` (dialogue fba18433). Nothing returned. Re-post D after P15d1 lands.
