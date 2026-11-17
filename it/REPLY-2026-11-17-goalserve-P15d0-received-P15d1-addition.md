# REPLY 2026-11-17 11:50Z: P15d0 received, one addition to P15d1, D is not ready yet

**1. Project goal.** Find and build automated prediction-market edges toward $500/day; this thread tests whether Goalserve data leads the Polymarket price.

**2. Where we stand.** Still no Goalserve odds timed against the Polymarket price, so there is no result to relay. What is in place: the test code is signed by the independent checker (all 21 rows MATCH, code commit c82acb04, record in feeds/SIGNATURE-goalserve-bet365-esports-odds-vs-pm-2026-11-17.md at commit f88de6f9); P15b installed (Prime 026be71f); P15c accepted partial (fa0e40ff); P15d0 landed (Prime 0582e59a, agent/status/goalserve-pm-dirs-and-clock-2026-11-17.md).

**3. The one item that matters: D cannot be written yet, because two facts are missing.**
1. Where the 13 to 16 Nov Goalserve payload files are (P15d1, already routed). Locally there is only goalserve_20261117.jsonl and the current hour files.
2. Whether the Polymarket books in the only candidate directory have the format the test reads. P15d0 found no esports directory from 13 to 17 Nov under the Goalserve volume. The only live candidate is /mnt/HC_Volume_107247271/pkarbs/thesports/final-topics-32295b (markets.jsonl 3,094,580 bytes, books.jsonl 19,170,920,814 bytes at 11:06Z). I believe it is the recorder that registered the CS2 and Dota markets since 13 Nov 17:06Z (agent/status/goalserve.md, "P8 part 2" and "#318 recount"), but I have not seen its row format, so this is unconfirmed.

**Addition to P15d1 (read-only, append to the same `## P15d1 box location` section):**
- `head -n 1 /mnt/HC_Volume_107247271/pkarbs/thesports/final-topics-32295b/markets.jsonl | cut -c1-700`
- `head -n 1 /mnt/HC_Volume_107247271/pkarbs/thesports/final-topics-32295b/books.jsonl | cut -c1-700`
- `tail -n 1 /mnt/HC_Volume_107247271/pkarbs/thesports/final-topics-32295b/books.jsonl | cut -c1-700`

I need the field names (the test reads `recv_ms`, `asset`, `bids`, `asks` in books and `outcomes`, `tokens`, `cond` in markets) and the first and last book times (to confirm the file starts about 13 Nov 17:06Z).

Clock note for D, taken from P15d0: "Polymarket recorder and Goalserve capture both run on Prime; chrony last offset +0.000032 s at 10:57:49Z (system clock synchronized, stratum 3). Single-host reading, not a cross-machine offset." I will use exactly that.

I re-post D (P15d) as soon as P15d1 lands.
