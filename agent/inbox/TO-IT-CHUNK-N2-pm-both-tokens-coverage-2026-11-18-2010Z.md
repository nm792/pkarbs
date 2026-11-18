# CHUNK N2: does the Polymarket recorder hold BOTH tokens' own books for every market? Read-only. Posted 18 Nov 2026 20:10Z.

**1. Goal.** The Dota thread says its shadow recorder holds the YES book only (coordinator, 19:52Z). SETTLED A1: each token is priced from its own book, never NO from YES. The Goalserve tests read the rising team's own token and a random token for the placebo, so both tokens' books must exist.
**2. Position.** From the code: `live/thesports/capture.py` adds BOTH tokens of every market to its book list (`for tk, o in zip(toks, outs)`) and fetches each token's own book from the CLOB, one row per changed book. If `final-topics-32295b` was written by that script, both sides are recorded. I have not seen the data, so this is unverified until this chunk runs. Tested here on a fake dir.
**3. The one item.** From the clean export, post the output under `## N2 token coverage (18 Nov)` in agent/status/goalserve.md:
```
V=/mnt/HC_Volume_107257520
nice -n 19 timeout 1800 python3 -I $X/feeds/pm_token_coverage.py $V/pkarbs/thesports/final-topics-32295b 3000000000; echo exit=$?
```
It reads the last 3 GB of books.jsonl (the newest days) and all of markets.jsonl; nothing is written.
**Done check:** `exit=0` and one line per sport with `both-tokens`, `one-token-only`, `no-books` and rows for token0 and token1. "one-token-only" above a few percent means that side is not testable for those markets; say it plainly, do not fill NO from YES.
