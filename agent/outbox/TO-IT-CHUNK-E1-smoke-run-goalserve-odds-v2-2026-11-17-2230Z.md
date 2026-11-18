# P18 — Goalserve odds v2 E1 smoke

Status: **run attempted; required smoke pass condition not met.**

- Data-volume gate passed at 06:14Z: 26,427,822,080 bytes available (>20 GB).
- Exported `feeds/` from the fetched project branch tip `7ca1509d736a2349c3097c0b58b8da1b3fcfcfeb` into a fresh scratch directory; the checkout was not modified. Source SHA-256: `goalserve_odds_vs_pm_v2.py` `8885752f54c3dc0c13cc0b60270fa76698b2fc1aca1746b8e1f8f95357f5fd4c`; test `04f46d566359930851db9a8cfb77dd2453b4c90b4c346bc85aa3053275d3f6b1`.
- `py_compile` passed and the self-test printed `ALL PASS`.
- Smoke command exited 1 at 06:18Z. Exact output: `look K=-1 is outside 1..20 (no complete UTC day since 2026-11-18 or past the last look)`. No `smoke.json` was produced; therefore `files > 0` and `NO_TRACEBACK` pass criteria were not established. The final 600 bytes had no traceback/error text, but this does not change the failed run.
- No cells or verdicts were read or reported. No other data-volume job was started by this run.

Evidence: `agent/status/goalserve.md` section `E1 smoke (18 Nov 06:14Z)`; self-test and smoke logs in the P18 scratch output directory on the data volume.
