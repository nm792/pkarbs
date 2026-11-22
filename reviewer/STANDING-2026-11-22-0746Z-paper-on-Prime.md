# STANDING RULE 2026-11-22 07:46Z: paper trades and paper-trade backtests run on Prime, under IT's caps (Nick 07:42Z)

Source: Nick 07:42Z 22 Nov: "why would we not run this on Prime where it needs to be eventually?" and "same with temperature. we don't build paper trades in fake platforms". Applies to every project (Temperature, MFW, PK arbs, Webb, ASX).

**Rule:**
1. Every paper trade, paper-trade forward test and paper-trade backtest runs on **Prime**, the platform where trading will live. Never in a Claude session container (/tmp/claude-*, /home/user, sandbox), and never in a stand-in setup.
2. It is deployed by IT from a pinned SHA into a Prime directory, and runs under IT's resource caps (memory cap, CPU nice/quota, oom_score_adj so the live recorders are never starved).
3. It posts a 15-min HEALTH READ at every start (IT-OPS-2026-11-22-0716Z-STANDING).
4. Session containers may still be used for code, unit tests and read-only analysis of data that was already recorded. Any number presented as paper P&L must come from a run on Prime.
5. Jobs running elsewhere now: declare them, and file a move plan with IT (why, what Prime needs, timings). They keep running until cut-over, and their results are labelled "off-Prime" until then.
