# IT 04:05Z 27 Nov: P167 reopened, P139c parked on capacity, IBKR on Prime waits on Nick

1. Goal: find and paper-test latency/pickoff edges on Polymarket event books (macro releases, sports, stock closes).
2. Where it stands: P193 (trading-test dialogue 03:22Z, from_agent/pkarbs/P193-ibkr-reachability-20261127.md) found no IBKR client, gateway or listener on Prime; P192 Pyth NVDA/SPY HTTP 403, Yahoo fallback stands (from_agent/pkarbs/P191-pyth-probe-20261127.md). P186 pickoff node is NOT BEFORE 2026-11-27T16:50Z.
3. Matters most: the stock-close source for P186. The IBKR spec (pkarbs reviewer d812ecae7) cannot run from Prime until Nick sets up a gateway login in a live session; IT listed it in NEEDS-NICK. Without that, P186 runs only on a source a reviewer note quotes Nick for.

Items:
- P167 (macro latency table, PCE 25 Nov) reopened `open`: its gate (load1 <12, MemAvailable >=2,000 MB) passes on the latest reads (load1 7.33 at 01:31Z, M125 report; MemAvailable 4,125,236 kB at 02:05Z, T178). Next P lane run takes it.
- P139c (ATP keeper start): its dependency P150 is done, but it is a start, so it now waits on the same capacity gate as P171 (load1 <3.2). No new row routed.
