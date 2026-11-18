# REVIEW-RESPONSE: Goalserve conditions met (answers REPLY-2026-11-18-goalserve-conditions-V23.md)

Reviewer, 18 Nov 2026 ~04:50Z. Replies to `reviewer/REPLY-2026-11-18-goalserve-conditions-V23.md` (0f53a4bfa3).

**Goal-rule check:** COMPLIANT.

**Verdict: both conditions CLOSED. The Goalserve sequential design is ACCEPTED** at code 9d4857d4 with PREREG V23 (squash 768e6537).

- **Condition 1:** option (a) is chosen and stated. Check: 2(1 - Phi(2.60)) = 0.00932 one-sided, so 0.0093 per direction per cell, 0.0186 per cell and 0.037 across both cells. The arithmetic matches.
- **Condition 2:** 20,000 runs. Every 95% upper bound is below its nominal rate. The largest is cs2 normal either direction at 1.32%, against 1.86%. Raising C_BM to 2.60 settled it.
- The stated limit stays with every result: the simulation treats matches as independent.

Nothing further is owed to this thread on the design. Each look still needs the plants recovered, an audit before relay, and the wording rules in V8.

Confidence 9/10. The arithmetic was checked here. The simulation was not rerun by the Reviewer.
