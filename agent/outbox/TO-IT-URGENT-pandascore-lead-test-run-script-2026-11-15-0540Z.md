APPROVALS NEEDED: None. Reviewer input is needed to reconcile the registered PM capture schema with the supplied runner; no code was changed.
RESULT
- **CRITICAL — no valid lead result:** the live PM capture uses `tk`/`ms` book fields and `q`/`tokens` market fields; `feeds/ps_lead_test.py` requires `asset`/`recv_ms` and `kind`/`vol`. Direct matching and pre-registered volume strata cannot be computed without an adapter and volume source.
- The live PandaScore raw directory currently contains three 15 Nov hourly files (4 match IDs and 27 counter increases; 2 exact normalized-name joins). The historical recount input is available separately in `/vol2/pkarbs/scratch/p318-recount/pandascore/`: a bounded scan found 23 match IDs and 1,912 counter increases, and exact team-name pairs join to the live PM market metadata. The historical book export is present as `share/books.jsonl.gz`, but has the same incompatible `tk`/`ms` schema; it does not supply a market-volume field.
- Prior 14 Nov recount: CS2 702 round changes; Dota 1,069 kills, 243 towers, 76 barracks and 38 Roshan increases. No full-window lead cells or verdicts were computed; independent audit not run. The 07:30Z deadline was missed.
DATA
- `agent/status/pandascore-lead-test-2026-11-15.json` — measured setup/schema facts and partial counts.
- Inputs inspected: `/vol2/pkarbs/pandascore/raw/` and `/vol2/pkarbs/thesports/final-topics-32295b/{markets,books}.jsonl`.
OPEN / NOT VERIFIED
- Three-match setup table with PM mids, full `cells` table and lead test remain unverified; no pass/fail claim is made. PM book timing resolution was not independently measured (STANDARD v1 cites 0.1–2 s latency).
- Reviewer: provide/approve a runner input adapter matching the actual PM schema and a per-market volume source; do not infer missing strata.
Count: notes run 1 (partial), outstanding 1, PENDING open 0
