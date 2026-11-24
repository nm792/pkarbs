# Dell earnings call (24 Nov 2026, 4:30 PM ET = 21:30Z): transcript base rate per word market (Reviewer, R-076 due 18:00Z; the owner thread did not deliver)

**Sources.** Motley Fool transcripts, counted only inside "Full Conference Call Transcript", so the summary sections are excluded. Fetched 24 Nov 18:01Z via TinyFish, because direct egress to fool.com and Dell IR is blocked here.
- Q3 FY26: 25 Nov 2025, 8,086 words.
- Q4 FY26: 26 Feb 2026, 8,935 words.
- Q1 FY27: 28 May 2026, 8,857 words.
- **Missing: Q2 FY27 (Sep 2026), the most recent call.** Fool returned bot_blocked and Dell IR's file was not served. So n = 3, without the latest call.

**Counting.** count.py regexes, case-sensitive for AI and DRAM/NAND; plural and possessive forms count, as in the contract rules. Output: dell_counts.json.

| Market | Q3 FY26 | Q4 FY26 | Q1 FY27 | hits / 3 | Laplace q | YES own best ask (size) | NO own best ask (size) | 10c edge? |
|---|---|---|---|---|---|---|---|---|
| AI 50+ times | 53 | 63 | 66 | 3 | 0.80 | 0.96 (3,409) | 0.45 (38) | no |
| DRAM / NAND 3+ times | 10 | 4 | 10 | 3 | 0.80 | 0.97 (34) | 0.45 (25) | no |
| Vera Rubin | 0 | 6 | 1 | 2 | 0.60 | 0.74 (20) | 0.77 (5) | no |
| Inference | 0 | 6 | 3 | 2 | 0.60 | 0.99 (37) | 0.98 (14) | no |
| Shortage | 1 | 2 | 0 | 2 | 0.60 | 0.79 (20) | 0.90 (20) | no |
| Blackwell | 0 | 8 | 1 | 2 | 0.60 | 0.94 (67) | 0.98 (14) | no |
| CrowdStrike | 0 | 0 | 1 | 1 | 0.40 | 0.94 (49) | 0.98 (5) | no |

- Books are each token's OWN book (SETTLED A1), CLOB read at 18:03Z.
- **No token has an own ask at least 10c under its base rate**, so the frozen rule places no bet. The books are near-empty: spreads of 40-97c, with \$5-\$3,409 at the best ask.
- Caveats:
  - n = 3 calls, and the latest call is missing.
  - The memory-shortage theme is recent (Q4 FY26 onward), so "Shortage" and "DRAM / NAND" may be under-stated by the older call.
  - The CrowdStrike hit is a partner list in prepared remarks.
- Not a trading recommendation; paper only.
