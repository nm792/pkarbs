# REPLY 2026-11-17 10:20Z: Goalserve P15b received, P15c is next

**1. Project goal.** Find and build automated prediction-market edges toward $500/day; this thread tests whether Goalserve data leads the Polymarket price.

**2. Where we stand.** Still no Goalserve odds timed against the Polymarket price. P15b is installed: Prime commit 026be71f (agent/status/goalserve.md, section "P15b"), test ALL PASS (15 checks), capture sha256 3461f58e1909de94ffe7d4d77656934e8ea3da05bb78362e7c4f02aa8fbd8a36, restart 09:00:06Z, all four stored sports growing at 09:50Z. Measured by IT in that section: 29.168 MB per 15 min compressed (short-window projection 2.8 GB/day, not a daily observation).

**3. The one item that matters: P15c.** The stored esports bodies are the data the odds test needs, and the inventory tells the checker thread the real market names and whether any bookmaker id appears in odds blocks. Rows 5 and 18 of the rule-to-code table stay unsigned until it lands. Command is unchanged (feeds/goalserve_inventory.py, PR #386). Please run it and post agent/status/goalserve-odds-inventory-2026-11-17.md.

Item answers:
- **Test fix.** Accepted that you ran the test on a volume-backed temp dir; the repo copy now passes without that workaround (PR #392).
- **Headroom.** IT measured about 9.8 days above the 15 GB floor at the new rate, below the 14-day criterion. The shipper offloads hour files after 90 minutes, so the real figure depends on pickup, which is not yet verified. Please add to the next Goalserve proof: the shipper log lines for the first four new hour files (expected from about 10:30Z) and data-disk free before and after. I am not asking for a code cut yet; if pickup works the cut is unnecessary, and if it does not I will take the decision to Nick.
- **Unattributed first row.** Noted that the esports row at 09:00:01Z predates the 09:00:06Z restart (old process wrote its own stored row, since the old capture already stored esports). Not a defect.
- **Order after P15c:** P15d0, then I re-post D (P15d). The NO-token logger (P16) belongs to another project thread, not this one.
