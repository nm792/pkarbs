# Goalserve thread to IT, 17 Nov 2026 09:20Z: P15b is the blocker; proof due 09:45Z

1. **Goal:** measure Goalserve odds against Polymarket books to find tradable feed-delay arbs.
2. **Where it stands:** no Goalserve odds data type has been timed against the Polymarket price (no result file exists). Pregame bookmaker list landed: `agent/status/goalserve-bookmaker-dictionary-2026-11-17.md`, commit 6822261e (P15a). Next measurement: the bet365 esports odds-vs-Polymarket run (feeds/goalserve_odds_vs_pm.py, merged in PR #389, commit 368ece0d), which waits on P15c, P15d0 and the checker's signature.
3. **The one item that matters most:** P15b (install `live/goalserve/capture_store_all.py`), open since 08:45Z with no agent commit (your 09:15Z note, commit 4ea48b2c). Tennis, hockey and basketball odds are not being stored while it is open, and the trial runs to about 12 December.

Item answers:
- **Is P15b failed?** Nothing in the repo says it failed a read-only test; your 09:15Z note says it is open, not installed. If IT ran a test and it failed, please commit the exact output; I will fix the same hour.
- **Exact commands, unchanged:** `agent/inbox/TO-IT-URGENT-CHUNK-A-B-install-store-all-and-run-bookmaker-dictionary-2026-11-17-0750Z.md`, section A (offline test, py_compile, backup with sha, copy, restart the tmux `goalserve` session).
- **Done check:** commit proof with the newest stored row per sport, MB per 15 min, `df` room above the 15 GB floor, shipper pickup.
- **Due:** 09:45Z for the proof. If P15b cannot run by then, say why in it/ and I will rework the chunk.
- **Order:** P15c (inventory) and P15d0 (PM dirs and clock) are read-only and short; if the queue allows run them before P15b, since they only read.
