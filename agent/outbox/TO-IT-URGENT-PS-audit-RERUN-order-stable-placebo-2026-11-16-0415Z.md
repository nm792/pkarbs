APPROVALS NEEDED: None. Read-only; no code or live process changed.
RESULT
- Code commit `97ecb4a2f7`; independent audit run twice on the same 23-match input. Raw JSON MD5s: `af4f55c77018cd928590ae249df188e8` and `76db178b64eda5f62762c0d7c57e3b5c`; raw files differ only in JSON object-key order. Parsed objects and canonical JSON MD5 `304492c8e443c57b913ca2d7755e8ca9` are identical. Input SHA-256s unchanged.
- `ps_lead_test.py` ran once (exit 0): 23 matches, 1,911 increases, 18 exact joins, 5 unmatched. Results cite STANDARD v1.
- All events; medians in seconds. Difference is median(real)−median(placebo); CI is the match-bootstrap 95% interval.
| title | series | n | median real | median placebo | difference | CI95 | price after feed | locked word |
|---|---|---:|---:|---:|---:|---|---:|---|
| CS2 | map | 424 | -30.62 | 37.46 | -68.08 | [-86.14, -36.51] | 11.67% | no lead reproduced |
| CS2 | match | 528 | -29.02 | 39.02 | -68.04 | [-76.34, 14.42] | 12.50% | no lead reproduced |
| Dota 2 | map | 979 | -22.69 | 7.31 | -30.00 | [-48.39, 14.91] | 24.15% | no lead reproduced |
| Dota 2 | match | 1,114 | -14.14 | -1.16 | -12.98 | [-25.02, 4.51] | 30.79% | no lead reproduced |
DATA
- `agent/status/pandascore-lead-audit-2026-11-16.json`; `agent/status/pandascore-lead-test-2026-11-16.json`.
OPEN / NOT VERIFIED
- Audit computations match across runs, but byte-identical JSON output was not achieved: key ordering differs. No code was changed under this read-only instruction.
Count: notes run 1, outstanding 0, PENDING open 0
