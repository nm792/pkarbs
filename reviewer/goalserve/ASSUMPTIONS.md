# ASSUMPTIONS: Goalserve odds-vs-Polymarket look (Goalserve thread, 20 Nov 2026)

Machine-readable: `assumptions.csv` (input, value, status, source, used_by, blocks_what). Status: MEASURED, PUBLISHED, ASSUMED. MECHANICS: `MECHANICS.md` here.

**Rule applied:** nothing ASSUMED feeds a reported result. The look reports a yes/no on odds-before-price within +-60 s; its ASSUMED rows are analysis conventions pre-registered before the data (changing one is a new test). Execution inputs (send RTT, queue priority, own-fill broadcast, Goalserve latency vs the real event) are UNMEASURED or ASSUMED, so **no trade, fill, P&L or "lead of N seconds" claim is made.** Results stay UNCHECKED/exploratory until an independent checker signs.

Count: see csv (MEASURED 12, PUBLISHED 6, ASSUMED 9).

Items that block a trading claim: send RTT; queue priority; Goalserve latency vs event; bookmaker identity (vendor says bet365, payload `bm` empty); own-fill broadcast.
What measures each (owner Goalserve thread unless stated): RTT = 100 timed CLOB GETs on the server (PandaScore thread row); queue = venue docs or an own-order test (needs Nick's approval, none requested); Goalserve latency = needs a second vantage (live score feed) and is not planned; bookmaker = ask Goalserve in writing.
