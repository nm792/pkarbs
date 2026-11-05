# outbox/2026-11-05-oddspapi-hist — re-run 2 completion

## RESULT — **PASS**

- Re-run 2 (5 Nov 02:47Z, unit `oddspapi-hist-rerun2.service`, MemoryMax 300M) finished 03:10:15Z, ~23 min wall, 78.9 MB peak RAM, 50.1 s CPU.
- Final: **hist_ok 198 / 219** fixtures (done line: `{"ev":"done","fixtures":219,"hist_ok":198}`). 21 of 219 returned 404 "No historical odds found".
- Fixture universe pulled (kept finished fixtures, skipped table tennis pulls, esports first):
  - tennis 631, CS2 25, LoL 1, Dota 5.
- Pass bar check: hist_ok 198 >= 20 ✓; CS2/LoL >= 1 ✓ (25+1); tennis >= 10 ✓ (631).
- Output: `/root/oddspapi/2026-11-04b/` (hist/ 198 files, fixtures_*.json.gz, log.jsonl).
- Data tarball committed: `rn1/scores/oddspapi/2026-11-04/oddspapi_2026-11-04.tar.gz`.

## OPEN / NOT VERIFIED
- Re-run 2's hist data tarball at the rn1 path: verify the 03:10Z re-run 2 bundle (vs run-1 02:16Z bundle) is the one at the tip — dispatched concurrently.

Count: notes run 2 (run-1 FAIL + re-run-2 PASS), outstanding 0.
