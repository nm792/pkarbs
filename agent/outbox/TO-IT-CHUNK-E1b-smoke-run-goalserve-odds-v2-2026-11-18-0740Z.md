# CHUNK E1b — Goalserve v2 smoke

- Result: PASS. Source is the signed E1b code at `d3a8849a94`; SHA-256 `goalserve_odds_vs_pm_v2.py` `621f92a7e545b025cd043363a6a5d361b9cc26222b542fd37fc0e38cb7c9c5f2`, test `269fb9cd226182323d006c6ebba8eae9a2ff148278a11c032fb82beda4cb125c`.
- `py_compile`: `COMPILE_OK`; isolated self-test: `ALL PASS`, exit 0.
- Smoke on the specified 24 hourly files: exit 0 at 07:48:54Z; `files=24`; `smoke_not_a_result=True`; `NO_TRACEBACK`.
- An initial attempt against the stale G2 export failed with `unrecognized arguments: --smoke`. Replaced only the two source files in the clean export with the fetched signed E1b versions, verified their hashes, then reran successfully. No project checkout changes, code changes, or other data-volume job.
- No cells or verdicts were read or posted. Logs and JSON remain in the existing Prime data-volume smoke scratch directory.
