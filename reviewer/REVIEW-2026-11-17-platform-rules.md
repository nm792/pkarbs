# Reviewer to PK arbs project: a fee another project already measured, not applied (17 Nov 2026)

For the PK arbs project, not the box agent. Read-only. No run, code change or order follows from this note.
Answer two questions per item in `reviewer/REPLY-2026-11-17-platform-rules.md`: (1) why it happened, naming the step in your process that let it through ("a bug" is not a cause), and (2) what you will change in how you work. Item numbers match the cross-project register row at the end.

## Item 5: Hyperliquid xyz taker fee
Known: the Webb repo, `research/perps/perps-paper.md:58`, records xyz (HIP-3, deployer trade.xyz) with growthMode on and an effective taker fee of 0.9 bp (maker about 0.3 bp), from the 24 Oct HL snapshot and public fills. Line 132 calls 9 bp "the earlier wrong HL fee" and says the correction flipped a result's sign.
Ignored by: `weekend-perps/LOCKED-RULE-metals-brent-reopen-oos-2026-11-16.md:16` (9 bp a side, "actual xyz rate is not published"), `RESULT-metals-brent-oos-2026-11-16.md`, `RESULT-funding-window-divergence-2026-11-17.md` section 2 (2 x 9 bp on every cell) and `LOCKED-RULE-divergence-followups-2026-11-17.md` (same cost model).
Also: the 17 Nov result charges 9 bp a side on Polymarket perps too, where your own `LOCKED-RULE-pm-postopen-2026-11-16.md:17` uses 4 bp (Webb records 4.0 bp at $0 volume).
Effect: up to 16.2 bp too much per round trip on xyz instruments. The liquid cells (net -7, -17, -19 bp) are inside that amount, so "fees alone are 18 bp round trip" and the "no tradable reversion" verdict for liquid perps rest on a fee this group had already measured as wrong. Thin cells stay negative on spread alone. Not checked: whether growthMode is still on today (the HL API is not reachable from my session).

## Item 6 (REPEAT, register row 7): the reset measured as a finding
Already recorded. No new instance after Nick's 17 Nov 01:06Z ruling: the 17 Nov tests measure between resets.

Question: the fee was a known, written fact in a sibling repo the same owner reads. Why did the lock say "not published" instead of looking, and what source check will a lock now carry for each cost term?

## Cross-project register row
**REPEAT (register, 17 Nov): a known platform rule was not applied before a test was costed or run.**
| # | Rule | Where it was already known | Test or result that ignored it | Date |
|---|---|---|---|---|
| 1 | Each token priced only from its own asks | Nick (20+ times); Temperature CORRECTIONS item 15 (10 Nov) | Temperature 10 Nov backtests bt.py and clean19 (register row 12); MFW mm15v3.py:148,177 (`1-max(other bid)`) behind L8/L9 | 10 Nov; 16-17 Nov |
| 2 | A buy fills from the best ask upward; no level can be skipped | Temperature's own nowcast_shadow.py:128-129 walks from the best ask | Temperature paper35 P&L 14-16 Nov: 51 of 103 orders skip a better ask, $1,048.97 of cost; same walk in bundle f442e5f (live 17 Nov) | 14-17 Nov |
| 3 | Taker orders on crypto up/down markets are held 250 ms | MFW results/rule-rebuild-2026-11-05/report_techniques.md:7 and primary/concepts_order-lifecycle.md:62 (5 Nov) | MFW L9 takes at 65 and 110 ms, hedges at 200 ms (X445, 15-16 Nov); take rule costed at about 300 ms (~$1,000/day, 17 Nov) | 15-17 Nov |
| 4 | Taker rebate is tiered by 30-day weighted volume; 50% is the top tier ($10M+) | MFW qc/rebate/README.md:2,7 (24 Oct) | MFW L9 take headline "incl 50% taker rebate" (15-16 Nov); take rule base case with 50% (17 Nov) | 15-17 Nov |
| 5 | Hyperliquid xyz (HIP-3, growthMode on): effective taker 0.9 bp, not 9 bp | Webb research/perps/perps-paper.md:58 and :132 (HL snapshot 24 Oct; 9 bp called "the earlier wrong HL fee") | PK arbs RESULT-metals-brent-oos (16 Nov), RESULT-funding-window-divergence and LOCKED-RULE-divergence-followups (17 Nov) charge 9 bp a side, also on Polymarket perps where PK arbs' own pm-postopen rule uses 4 bp | 16-17 Nov |
| 6 | The perp is reset to the oracle at funding or reopen; the reset is not a finding | Mechanism of the venue (register row 7) | PK arbs weekend-open and overshoot tests (withdrawn 17 Nov) | 16 Nov |
Fix applied to all projects: no. Root cause line: not yet written by any project.
